"""Polling coordinator: one per config entry, i.e. one per operator.

Fetches the operator's GTFS-Realtime positions (and trip updates where the
operator publishes useful ones), parses them with the operator's adapter, and
hands the observations to Fleet, which decides what is published.

! THE KEY RIDES IN THE URL for operators that take it as a query parameter,
and aiohttp puts the full URL, query included, into its exception text. So no
exception from a request is ever logged or re-raised with its message: only
its TYPE. Never log `err`, `str(err)` or `resp.url` here.
"""

from __future__ import annotations

import logging
import time
from datetime import timedelta
from functools import partial
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    CONF_SHOW_PARKED,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SHOW_PARKED,
    MAX_TRANSIENT_FAILURES,
    REQUEST_TIMEOUT,
    USER_AGENT,
)
from saw_livetrack.digitraffic_rail import DigitrafficError
from saw_livetrack.renfe import RenfeError
from saw_livetrack.entur import EnturError
from saw_livetrack.gtfs import Fleet, decode
from saw_livetrack.trafikverket import AuthRefused, KeyedError
from saw_livetrack.irish_rail import KeyedError as IrishRailError
from saw_livetrack.ns import AuthRefused as NsAuthRefused, KeyedError as NsKeyedError
from saw_livetrack.tfnsw import AuthRefused as TfnswAuthRefused, KeyedError as TfnswKeyedError
from . import entur_push, irish_runs, ns_lines, plausible, poll, rail, shapepath, sweden_lines, tracknet, tunnel
from .operators import Operator
from .operators.base import (SOURCE_DIGITRAFFIC, SOURCE_ENTUR, SOURCE_IRISH_RAIL, SOURCE_NS, SOURCE_RENFE,
                             SOURCE_TFNSW, SOURCE_TRAFIKVERKET)
from .shared_digitraffic_rail import get_shared_rail_client, release_shared_rail_client
from .shared_irish_rail import get_shared_irish_rail_client, release_shared_irish_rail_client
from .shared_ns import get_shared_ns_client, release_shared_ns_client
from .shared_renfe import get_shared_renfe_client, release_shared_renfe_client
from .shared_entur import get_shared_entur_client, release_shared_entur_client
from .shared_trafikverket import get_shared_trafikverket_client, release_shared_trafikverket_client
from .shared_tfnsw import get_shared_tfnsw_client, release_shared_tfnsw_client
from saw_livetrack.gtfs import next_stops as next_stops_from
from saw_livetrack.gtfs import stop_delays, trip_coverage
from .schedule import timetable_stale
from .statics import StaticTimetable

_LOGGER = logging.getLogger(__name__)


class AuthError(Exception):
    """The operator refused the key (HTTP 401 or 403)."""


async def fetch_feed(session: aiohttp.ClientSession, url: str,
                     params: dict[str, str] | None):
    """Fetch and decode one GTFS-RT feed.

    Returns the FeedMessage, or None on any failure. Raises AuthError on 401
    or 403, which is the one failure retrying cannot fix.
    """
    try:
        async with session.get(
            url, params=params, headers={"User-Agent": USER_AGENT},
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
        ) as resp:
            if resp.status in (401, 403):
                raise AuthError
            if resp.status != 200:
                _LOGGER.debug("feed answered HTTP %s", resp.status)
                return None
            raw = await resp.read()
    except AuthError:
        raise
    except (aiohttp.ClientError, TimeoutError) as err:
        _LOGGER.debug("feed fetch failed: %s", type(err).__name__)
        return None
    feed = decode(raw)
    if feed is None:
        _LOGGER.debug("feed decode failed")
    return feed


def key_params(op: Operator, data: dict[str, Any]) -> dict[str, str] | None:
    if not op.needs_key:
        return None
    return {op.key_param: data.get(CONF_API_KEY, "")}


class CommuterRailCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """One poll of one operator's feed per cycle, shared by every platform."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, op: Operator) -> None:
        opts = {**entry.data, **entry.options}
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{entry.domain} {op.id}",
            update_interval=timedelta(
                seconds=int(opts.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))),
        )
        self.operator = op
        self._params = key_params(op, dict(entry.data))
        self._show_parked = bool(opts.get(CONF_SHOW_PARKED, DEFAULT_SHOW_PARKED))
        self._session = async_get_clientsession(hass)
        self.fleet = Fleet(styling=op.styling,
                           **({} if op.stall_m is None else {"stall_m": op.stall_m}))
        # Renfe (Spain, SSOT 10): the ONE shared client per Home Assistant, registered
        # as this operator's consumer; it also hands over its copy of the timetable.
        # Renfe's fixes bounce back and forth and onto other lines (plausible.py).
        self._plausible = plausible.Plausible() if op.plausible else None
        self._renfe = None
        if op.source == SOURCE_RENFE:
            self._renfe = get_shared_renfe_client(hass, op.renfe_consumer)
        # Entur (Norway, SSOT 12): the ONE shared client per Home Assistant, this operator's (consumer, codespace)
        # claimed; its timetable is the client's copy on disk (Vy's is 66 MB), read only when it is distilled.
        self._entur = None
        if op.source == SOURCE_ENTUR:
            self._entur = get_shared_entur_client(hass, op.entur_consumer, op.entur_codespace)
        # Irish Rail (Ireland, SSOT 13): the ONE shared client per Home Assistant, this operator's consumer claimed; its
        # copy of the NTA's timetable on disk is the one distilled here (cut to the P/D trips); the runs drawn from it
        # (irish_runs.py), every one an estimate.
        self._irish = None
        self._irish_runs: irish_runs.IrishRuns | None = None
        self._irish_version: Any = None
        if op.source == SOURCE_IRISH_RAIL:
            self._irish = get_shared_irish_rail_client(hass, op.irish_rail_consumer)
            self._irish_runs = irish_runs.IrishRuns()
        # Transport for NSW (SSOT 16): the ONE shared client per Home Assistant, this operator's consumer registered with
        # the key stored in this entry; its copy of the timetable on disk is the one distilled here.
        self._tfnsw = None
        self._tfnsw_version: Any = None
        self._tfnsw_version2: Any = None
        if op.source == SOURCE_TFNSW:
            self._tfnsw = get_shared_tfnsw_client(hass, op.tfnsw_consumer, str(entry.data.get(CONF_API_KEY, "")))
            if op.tfnsw_sydney_trains:
                # Asked at every claim, right after it (saw-livetrack 0.2.37); the last release forgets it.
                self._tfnsw.set_sydney_trains(op.tfnsw_consumer, True)
        raw_source = None
        if self._tfnsw is not None:
            raw_source = partial(self._tfnsw_zip, op.tfnsw_timetable)
        elif self._renfe is not None:
            raw_source = self._renfe.static_zip
        elif self._entur is not None:
            raw_source = self._entur_zip
        elif self._irish is not None:
            raw_source = self._irish_zip
        self._static = StaticTimetable(hass, self._session, op, raw_source=raw_source)
        # A second timetable beside the first (NSW: Sydney Trains' Intercity cut, SSOT 16), merged before use.
        self._static2: StaticTimetable | None = None
        self._merged_key: tuple[Any, Any] | None = None
        self._merged: dict[str, Any] | None = None
        second = op.static_second
        if second is not None and self._tfnsw is not None:
            self._static2 = StaticTimetable(hass, self._session, second,
                                            raw_source=partial(self._tfnsw_zip, second.tfnsw_timetable))
        # Trains pushed through Oslo's tunnels where their fixes freeze (entur_push.py).
        self._entur_push = entur_push.EnturPush() if op.entur_push else None
        self._failures = 0
        self._last_good: dict[str, Any] | None = None
        self.feed_timestamp: int | None = None
        self.trip_coverage: tuple[int, int] | None = None
        self._timetable_stale = False
        self._rail_loaded = False
        self.rail_segments: int | None = None
        self._rail_check: rail.RailCheck | None = None
        self.track_lines: int | None = None
        self._track_path = None
        # Trains pushed through tunnels where their fixes stop (tunnel.py; SSOT 8.3).
        self._push: tunnel.TunnelPush | None = None
        self.tunnel_ways: int | None = None
        # Digitraffic (Finland): the ONE shared client per Home Assistant, with this
        # operator's consumer registered (saw-livetrack 0.2.7; release() gives it back).
        self._rail_client = None
        if op.source == SOURCE_DIGITRAFFIC:
            self._rail_client = get_shared_rail_client(hass, op.digitraffic_consumer)
        # Trafikverket (Sweden, SSOT 14): the ONE shared client per Home Assistant, this operator's (consumer, brand)
        # claimed with the key stored in this entry; the runs it keeps and the lines they run along (sweden_lines).
        self._trv = None
        self._trv_runs: sweden_lines.RunFilter | None = None
        self._trv_geo: sweden_lines.SwedenGeometry | None = None
        if op.source == SOURCE_TRAFIKVERKET:
            self._trv = get_shared_trafikverket_client(hass, op.trafikverket_consumer, op.trafikverket_brand,
                                                       str(entry.data.get(CONF_API_KEY, "")))
            self._trv_runs = sweden_lines.RunFilter()
            self._trv_geo = sweden_lines.SwedenGeometry(op.extra.get("fallback_stops", ()))
        # NS (the Netherlands, SSOT 15): the ONE shared client per Home Assistant, this operator's consumer claimed with
        # the key stored in this entry; the lines its trains run along (ns_lines).
        self._ns = None
        self._ns_geo: ns_lines.NsGeometry | None = None
        if op.source == SOURCE_NS:
            self._ns = get_shared_ns_client(hass, op.ns_consumer, str(entry.data.get(CONF_API_KEY, "")))
            self._ns_geo = ns_lines.NsGeometry()

    def release(self) -> None:
        """Give back this entry's claim on the shared Digitraffic client. On the event
        loop; safe to call twice."""
        if self._rail_client is not None:
            self._rail_client = None
            release_shared_rail_client(self.hass, self.operator.digitraffic_consumer)
        if self._renfe is not None:
            self._renfe = None
            release_shared_renfe_client(self.hass, self.operator.renfe_consumer)
        if self._entur is not None:
            self._entur = None
            release_shared_entur_client(self.hass, self.operator.entur_consumer,
                                        self.operator.entur_codespace)
        if self._trv is not None:
            self._trv = None
            release_shared_trafikverket_client(self.hass, self.operator.trafikverket_consumer,
                                               self.operator.trafikverket_brand)
        if self._irish is not None:
            self._irish = None
            release_shared_irish_rail_client(self.hass, self.operator.irish_rail_consumer)
        if self._ns is not None:
            self._ns = None
            release_shared_ns_client(self.hass, self.operator.ns_consumer)
        if self._tfnsw is not None:
            self._tfnsw = None
            release_shared_tfnsw_client(self.hass, self.operator.tfnsw_consumer)

    def _tfnsw_zip(self, timetable: str | None = None) -> bytes | None:
        """The shared TfNSW client's copy of `timetable` (None: nswtrains), or None before it has one (blocking: the
        executor; StaticTimetable asks again in SOURCE_WAIT_S)."""
        client = self._tfnsw
        if client is None:
            return None
        path = client.static_path(timetable) if timetable else client.static_path()
        if path is None:
            return None
        with open(path, "rb") as fh:
            return fh.read()

    def _tfnsw_version_of(self, timetable: str | None) -> Any:
        client = self._tfnsw
        return client.static_version(timetable) if timetable else client.static_version()

    def _read_tfnsw(self) -> tuple[Any, Any, Any, Any]:
        """(positions, trip updates, the version of the client's copy each timetable is distilled from, the second's or
        None). Blocking: the executor. Raises the client's errors."""
        op = self.operator
        client = self._tfnsw
        positions, updates = client.for_consumer(op.tfnsw_consumer)
        second = op.static_second
        return (positions, updates, self._tfnsw_version_of(op.tfnsw_timetable),
                self._tfnsw_version_of(second.tfnsw_timetable) if second is not None else None)

    def _static_data(self) -> dict[str, Any] | None:
        """The timetable everything reads: the first, or the first and second merged (op.static_merge), the merge kept
        until either is replaced, so caches keyed on the timetable's identity hold."""
        first = self._static.data
        if self._static2 is None or self.operator.static_merge is None:
            return first
        second = self._static2.data
        # The objects themselves, never their id(): a freed timetable's id can be reused by its successor.
        key = self._merged_key
        if key is None or key[0] is not first or key[1] is not second:
            self._merged_key = (first, second)
            self._merged = self.operator.static_merge(first, second)
        return self._merged

    async def _fetch_tfnsw(self):
        """(positions, trip updates, version) from the shared TfNSW client, or None on a failed fetch. Every key refused
        for 10 minutes asks the user for a new one. Only the exception's TYPE is logged: the key is in a header, never in
        a message."""
        op = self.operator
        try:
            return await self.hass.async_add_executor_job(self._read_tfnsw)
        except TfnswAuthRefused as err:
            raise ConfigEntryAuthFailed(f"{op.name}: Transport for NSW refused the key") from err
        except TfnswKeyedError as err:
            _LOGGER.debug("%s feed failed: %s", op.id, type(err).__name__)
            return None

    @property
    def tfnsw_stats(self) -> dict[str, Any] | None:
        """The shared TfNSW client's counters, for diagnostics; None for other sources. Never a key."""
        return self._tfnsw.stats() if self._tfnsw is not None else None

    def _read_ns(self) -> tuple[list, dict[str, Any]]:
        """(this operator's trains, the geometry). Blocking: the executor. Raises the client's errors."""
        op = self.operator
        client = self._ns
        trains = client.for_consumer(op.ns_consumer, op.id)
        static = self._ns_geo.update(trains, client.stations(), client.pair_lines(), client.static_version())
        return trains, static

    async def _fetch_ns(self):
        """(trains, geometry) from the shared NS client, or None on a failed fetch. Every key refused for 10 minutes
        asks the user for a new one. Only the exception's TYPE is logged."""
        op = self.operator
        try:
            return await self.hass.async_add_executor_job(self._read_ns)
        except NsAuthRefused as err:
            raise ConfigEntryAuthFailed(f"{op.name}: NS refused the key") from err
        except NsKeyedError as err:
            _LOGGER.debug("%s feed failed: %s", op.id, type(err).__name__)
            return None

    @property
    def ns_stats(self) -> dict[str, Any] | None:
        """The shared NS client's counters, for diagnostics; None for other sources. Never a key."""
        if self._ns is None:
            return None
        return {**self._ns.stats(), "patterns": len(self._ns_geo.data.get("rail_shapes") or ())}

    def _irish_zip(self) -> bytes | None:
        """The shared Irish Rail client's copy of the NTA's zip, or None before it has one (blocking: the executor;
        StaticTimetable asks again in SOURCE_WAIT_S)."""
        client = self._irish
        path = client.static_path() if client is not None else None
        if path is None:
            return None
        with open(path, "rb") as fh:
            return fh.read()

    def _read_irish(self, static: dict[str, Any] | None) -> tuple[list, Any]:
        """(the runs drawn this poll, the client's timetable version). Blocking: the executor. Raises the client's
        errors (a failed read of the trains); the station list is the client's last copy when its weekly read fails."""
        op = self.operator
        client = self._irish
        trains = client.for_consumer(op.irish_rail_consumer)
        api = client.stations()
        rows = self._irish_runs.poll(trains, api, client.stations_version(), static, time.time())
        return rows, client.static_version()

    async def _fetch_irish(self):
        """(rows, timetable version) from the shared Irish Rail client, or None on a failed read. Keyless: only the
        exception's TYPE is logged, as for every feed here."""
        try:
            return await self.hass.async_add_executor_job(self._read_irish, self._static.data)
        except IrishRailError as err:
            _LOGGER.debug("%s feed failed: %s", self.operator.id, type(err).__name__)
            return None

    @property
    def irish_rail_stats(self) -> dict[str, Any] | None:
        """The shared Irish Rail client's counters and this entry's runs, for diagnostics; None for other sources."""
        if self._irish is None or self._irish_runs is None:
            return None
        runs = self._irish_runs
        return {**self._irish.stats(), "drawn": len(runs.rows), "unplaced": runs.unplaced,
                "skipped": dict(runs.skipped), "ghosts": runs.tracker.ghosts, "early": runs.tracker.early}

    def _read_trafikverket(self) -> tuple[list, dict[str, Any]]:
        """(the runs kept, the geometry) for this operator's claim. Blocking: the executor. Raises the client's
        errors."""
        op = self.operator
        runs = self._trv.for_consumer(op.trafikverket_consumer, op.trafikverket_brand)
        stations = self._trv.stations()
        kept = self._trv_runs.keep(runs, time.time())
        static = self._trv_geo.update(kept, stations, self._trv.stations_version())
        return kept, static

    async def _fetch_trafikverket(self):
        """(runs, geometry) from the shared Trafikverket client, or None on a failed fetch. Every key refused for
        10 minutes asks the user for a new one. Only the exception's TYPE is logged: no message carries the key, which
        travels in the request body."""
        op = self.operator
        try:
            return await self.hass.async_add_executor_job(self._read_trafikverket)
        except AuthRefused as err:
            raise ConfigEntryAuthFailed(f"{op.name}: Trafikverket refused the key") from err
        except KeyedError as err:
            _LOGGER.debug("%s feed failed: %s", op.id, type(err).__name__)
            return None

    @property
    def trafikverket_stats(self) -> dict[str, Any] | None:
        """The shared Trafikverket client's counters and this entry's skips, for diagnostics; None for other
        sources. Never a key."""
        if self._trv is None:
            return None
        return {**self._trv.stats(), "skipped": dict(self._trv_runs.skipped),
                "shipped_pairs": self._trv_geo.shipped_pairs,
                "patterns": len(self._trv_geo.data.get("rail_shapes") or ())}

    def _entur_zip(self) -> bytes | None:
        """The shared Entur client's timetable zip for this operator's codespace, or None before it has one
        (blocking: the executor; StaticTimetable asks again in SOURCE_WAIT_S)."""
        client = self._entur
        path = client.static_path(self.operator.entur_codespace) if client is not None else None
        if path is None:
            return None
        with open(path, "rb") as fh:
            return fh.read()

    async def _fetch_entur(self):
        """(positions, trip updates) for this operator's consumer and codespace from the shared Entur client
        (blocking: the executor), or None on a failed fetch. Only the exception's TYPE is logged."""
        op = self.operator
        try:
            return await self.hass.async_add_executor_job(
                self._entur.for_consumer, op.entur_consumer, op.entur_codespace)
        except EnturError as err:
            _LOGGER.debug("%s feed failed: %s", op.id, type(err).__name__)
            return None

    @property
    def entur_stats(self) -> dict[str, Any] | None:
        """The shared Entur client's counters, for diagnostics; None for other sources."""
        return self._entur.stats() if self._entur is not None else None

    async def _fetch_renfe(self):
        """(positions, trip updates) for this operator's consumer from the shared Renfe
        client (blocking: the executor), or None on a failed fetch. Keyless: only the
        exception's TYPE is logged, as for every feed here."""
        op = self.operator
        try:
            return await self.hass.async_add_executor_job(
                self._renfe.for_consumer, op.renfe_consumer)
        except RenfeError as err:
            _LOGGER.debug("%s feed failed: %s", op.id, type(err).__name__)
            return None

    async def _fetch_digitraffic(self) -> list[dict[str, Any]] | None:
        """This operator's records from the shared client (blocking: the executor), or
        None on a failed fetch. The client's exceptions carry no secret (keyless), but
        only their TYPE is logged, as for every feed here."""
        op = self.operator
        try:
            return await self.hass.async_add_executor_job(
                self._rail_client.for_consumer, op.digitraffic_consumer)
        except DigitrafficError as err:
            _LOGGER.debug("%s feed failed: %s", op.id, type(err).__name__)
            return None

    @property
    def timetable(self) -> dict[str, Any] | None:
        info = self._static.info
        if self._static2 is not None:
            # Both cuts, for diagnostics (NSW: nswtrains' and Sydney Trains').
            return {"first": info, "second": self._static2.info}
        return info

    @property
    def plausible_stats(self) -> dict[str, int] | None:
        """Fixes refused and runs confirmed since start (plausible.py); None when off."""
        p = self._plausible
        return None if p is None else {"refused": p.refused, "confirmed": p.confirmed,
                                       "placeholders": p.placeholders}

    @property
    def renfe_stats(self) -> dict[str, Any] | None:
        """The shared Renfe client's counters, for diagnostics; None for other sources."""
        return self._renfe.stats() if self._renfe is not None else None

    @property
    def rail_shape_segments(self) -> int | None:
        return self._rail_check.shape_segments if self._rail_check else None

    def _check_timetable(self, hit: int, total: int) -> None:
        """Refresh the timetable early when it does not know the realtime
        feed's trips (Metra's GTFS static change renames every trip; delays
        computed from the old timetable vanish). One warning per episode."""
        self.trip_coverage = (hit, total)
        if timetable_stale(hit, total):
            self._static.request_refresh()
            if self._static2 is not None:
                self._static2.request_refresh()
            if not self._timetable_stale:
                self._timetable_stale = True
                _LOGGER.warning(
                    "%s: %s of %s realtime trips are not in the cached timetable; "
                    "refreshing it early. Delays are missing until they match",
                    self.operator.name, total - hit, total)
        elif self._timetable_stale and total:
            self._timetable_stale = False
            _LOGGER.info("%s: realtime trips match the timetable again (%s of %s)",
                         self.operator.name, hit, total)

    async def _async_update_data(self) -> dict[str, Any]:
        op = self.operator
        tu = None
        trv_static = None
        if op.source == SOURCE_TRAFIKVERKET:
            # The runs stand in for a feed, as Digitraffic's records: parse(runs) reads them. Sweden has no
            # timetable: the geometry the client's stations and the shipped lines make stands in for one.
            got = await self._fetch_trafikverket()
            feed, trv_static = got if got is not None else (None, None)
        elif op.source == SOURCE_NS:
            # The trains stand in for a feed, as Sweden's runs: parse(trains) reads them; the geometry their SpoorKaart
            # paths make stands in for a timetable (ns_lines.NsGeometry).
            got = await self._fetch_ns()
            feed, trv_static = got if got is not None else (None, None)
        elif op.source == SOURCE_RENFE:
            # Both feeds at once, already cut to this integration's consumer.
            got = await self._fetch_renfe()
            feed, tu = got if got is not None else (None, None)
        elif op.source == SOURCE_TFNSW:
            # Both feeds, already cut to route_type 100 and cleaned (trip updates None when that file failed). A new
            # timetable on the client's disk is distilled again at once, not at the day's refresh.
            got = await self._fetch_tfnsw()
            feed = None
            if got is not None:
                feed, tu, version, version2 = got
                if version != self._tfnsw_version:
                    if self._tfnsw_version is not None:
                        self._static.request_refresh()
                    self._tfnsw_version = version
                if self._static2 is not None and version2 != self._tfnsw_version2:
                    if self._tfnsw_version2 is not None:
                        self._static2.request_refresh()
                    self._tfnsw_version2 = version2
        elif op.source == SOURCE_ENTUR:
            # Both feeds, already cut to this consumer and codespace (trip updates None when that file failed).
            got = await self._fetch_entur()
            feed, tu = got if got is not None else (None, None)
        elif op.source == SOURCE_DIGITRAFFIC:
            # The client's records stand in for a feed: parse(records) reads them.
            feed = await self._fetch_digitraffic()
        elif op.source == SOURCE_IRISH_RAIL:
            # The runs drawn from the timetable stand in for a feed (irish_runs.py): parse(rows) reads them. A new
            # copy of the NTA's zip is distilled again within the hour, not at the day's refresh.
            got = await self._fetch_irish()
            feed = None
            if got is not None:
                feed, version = got
                if version != self._irish_version:
                    if self._irish_version is not None:
                        self._static.request_refresh()
                    self._irish_version = version
        else:
            try:
                feed = await fetch_feed(self._session, op.positions_url, self._params)
            except AuthError as err:
                raise ConfigEntryAuthFailed(f"{op.name} refused the key") from err

        if feed is None:
            self._failures += 1
            if self._failures <= MAX_TRANSIENT_FAILURES and self._last_good is not None:
                # Serve the last result rather than blanking the map. Every
                # entity carries observed_at, so a stale position reads as
                # stale rather than as current.
                return self._last_good
            raise UpdateFailed(
                f"{op.name} positions unavailable ({self._failures} consecutive failures)")
        self._failures = 0

        if not self._rail_loaded:
            # Once, off the event loop: the rail this railroad runs on (SSOT
            # 7.10). Without a file there is no check and nothing changes.
            self._rail_loaded = True
            # NARN covers US railroads only (Operator.narn); elsewhere the check is the
            # railroad's own shapes alone, at its own distance (off_rail_m; SSOT 9.1).
            idx = (await self.hass.async_add_executor_job(rail.load, op.id)
                   if op.narn else None)
            # NARN track OR the railroad's own route (rail.RailCheck): NARN lacks
            # lines newer than it, such as NICTD's Monon Corridor south of Hammond.
            self._rail_check = rail.RailCheck(idx, op.off_rail_m)
            self.fleet.on_rail = self._rail_check
            if idx is not None:
                self.rail_segments = len(idx)
            _LOGGER.debug("%s rail: %s segments", op.id, self.rail_segments)
            # The railroad's track network, where one ships (Finland, SSOT 8.3): the
            # card follows the tracks between fixes (D3c-v). Without one, nothing changes.
            net = await self.hass.async_add_executor_job(tracknet.load, op.id)
            if net is not None:
                self.track_lines = len(net)
                self._track_path = partial(tracknet.track_path, net)
                if op.tunnels and op.tunnel_clocks is not None:
                    # Each tunnel's way along the tracks, routed once (SSOT 8.3).
                    self._push = await self.hass.async_add_executor_job(
                        tunnel.TunnelPush, net, op.tunnels)
                    self.tunnel_ways = len(self._push.ways)
            _LOGGER.debug("%s tracks: %s lines, %s tunnel ways", op.id, self.track_lines,
                          self.tunnel_ways)

        # The timetable loads and refreshes in the background; until it has,
        # no next station is published and nothing else changes.
        if self._static.due():
            self.config_entry.async_create_background_task(
                self.hass, self._static.async_refresh(), f"{op.id} timetable")
        if self._static2 is not None and self._static2.due():
            self.config_entry.async_create_background_task(
                self.hass, self._static2.async_refresh(), f"{op.static_second.id} timetable")

        # Sweden's geometry for a Trafikverket operator (sweden_lines.SwedenGeometry), the cached timetable
        # otherwise (with its second merged in, op.static_second): everything below reads the one.
        static = trv_static if trv_static is not None else self._static_data()
        now = time.time()
        delays = None
        next_stops = None
        trip_delays = None
        if tu is None and op.trip_updates_url and (op.parse_delays or op.static_url):
            try:
                tu = await fetch_feed(self._session, op.trip_updates_url, self._params)
            except AuthError:
                tu = None
        if tu is not None and op.filter_trip_updates is not None:
            # This entry's own trips only (Renfe: every network in one feed).
            tu = op.filter_trip_updates(tu)
        # Renfe's trip updates came with its positions (SOURCE_RENFE).
        if tu is not None:
            # A skipped stop is never the next stop (poll.drop_skipped).
            poll.drop_skipped(tu)
            if op.parse_delays:
                delays = op.parse_delays(tu)
            # Delay at the next stop, one rule for every feed (backlog 275):
            # the update's own delay, else predicted minus scheduled, which
            # needs the timetable. Fleet prefers it to parse_delays.
            trip_delays = stop_delays(tu, static, now)
            if static is not None:
                self._check_timetable(*trip_coverage(tu, static))
                next_stops = next_stops_from(tu, static, now)
            if op.stops_from_updates is not None:
                # Norway: from the timetable plus the update's delays, never the origin.
                next_stops, trip_delays = op.stops_from_updates(tu, static, now)

        extras = None
        if op.parse_stops is not None:
            # Digitraffic: next stops and delays from each train's own timetable.
            next_stops, trip_delays, extras = op.parse_stops(feed, static, now)

        if self._rail_check is not None:
            self._rail_check.set_shapes(static)
        if (op.source not in (SOURCE_DIGITRAFFIC, SOURCE_TRAFIKVERKET, SOURCE_IRISH_RAIL, SOURCE_NS)
                and feed.header.HasField("timestamp")):
            self.feed_timestamp = int(feed.header.timestamp)
        # A fix older than the operator's limit is refused before Fleet sees it
        # (poll.fresh_only; SE Queensland's frozen fixes, SSOT 9.1).
        observations, stale = poll.fresh_only(op.parse(feed), now, op.max_fix_age_s)
        if op.obs_filter is not None:
            # The operator's own refusals (Norway: a finished run's train still in the feed).
            if op.obs_filter_updates:
                # NSW: a finished run's end moves with its latest delay.
                observations = op.obs_filter(observations, static, now, updates=tu)
            else:
                observations = op.obs_filter(observations, static, now)
        if self._plausible is not None:
            # Off the trip's own line, back along it or too fast: the last good fix.
            observations = self._plausible.filter(
                observations, static, now,
                untrusted=op.untrusted_fixes(feed) if op.untrusted_fixes is not None else ())
        result = self.fleet.update(
            observations, now,
            show_parked=self._show_parked, delays=delays, next_stops=next_stops,
            static=static, trip_delays=trip_delays)
        result["stale"] = stale
        # A fix this old never counts as standing (Finland's tunnel; SSOT 8.1).
        result["unstalled"] = poll.unstall_stale(result, observations, now,
                                                 op.stand_max_fix_age_s)
        poll.apply_extras(result, extras)
        # The operator's own touches after Fleet (SE Queensland: look, label, lateness
        # and the arrow, from the timetable; poll.decorate_all).
        poll.decorate_all(result, observations, static, op.decorate)
        if self._plausible is not None:
            # The arrow the way the trip's stops run, not the shape's order (C16).
            self._plausible.apply_arrows(result, observations, static)
        # Along the tracks from the last fix (D3c-v), after everything that moves or
        # replaces a position.
        if self._track_path is not None:
            result["track_paths"] = poll.add_track_paths(result, self._track_path)
        else:
            # No track network shipped: along each trip's own shape (shapepath; Lee
            # 2026-10-20, "A train cannot exist off of the tracks").
            result["track_paths"] = shapepath.add_shape_paths(result, observations,
                                                              static)
        if self._push is not None:
            # A train dark in a tunnel is pushed along it on its own stop times, after the
            # paths from the fixes: it replaces the position and the path (D3d, SSOT 8.3).
            names = (static or {}).get("stops") or {}
            counts = self._push.apply(result, observations, op.tunnel_clocks(feed), now,
                                      names)
            result["estimated"] = counts[tunnel.ESTIMATED]
        if self._entur_push is not None:
            # Norway: a frozen fix at one of Oslo's tunnels is pushed through it; elsewhere it is held (D3d).
            result["estimated"] = self._entur_push.apply(result, observations, static, now)
        if self._irish_runs is not None:
            # Irish Rail: every train a no-fix estimate along its trip's shape, last of all (D3d, irish_runs.py).
            result["estimated"] = self._irish_runs.publish(result)
        self._last_good = result
        return result
