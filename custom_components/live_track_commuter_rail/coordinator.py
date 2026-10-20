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
from saw_livetrack.gtfs import Fleet, decode
from . import poll, rail, shapepath, tracknet, tunnel
from .operators import Operator
from .operators.base import SOURCE_DIGITRAFFIC, SOURCE_RENFE
from .shared_digitraffic_rail import get_shared_rail_client, release_shared_rail_client
from .shared_renfe import get_shared_renfe_client, release_shared_renfe_client
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
        self._renfe = None
        if op.source == SOURCE_RENFE:
            self._renfe = get_shared_renfe_client(hass, op.renfe_consumer)
        self._static = StaticTimetable(
            hass, self._session, op,
            raw_source=self._renfe.static_zip if self._renfe is not None else None)
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

    def release(self) -> None:
        """Give back this entry's claim on the shared Digitraffic client. On the event
        loop; safe to call twice."""
        if self._rail_client is not None:
            self._rail_client = None
            release_shared_rail_client(self.hass, self.operator.digitraffic_consumer)
        if self._renfe is not None:
            self._renfe = None
            release_shared_renfe_client(self.hass, self.operator.renfe_consumer)

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
        return self._static.info

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
        if op.source == SOURCE_RENFE:
            # Both feeds at once, already cut to this integration's consumer.
            got = await self._fetch_renfe()
            feed, tu = got if got is not None else (None, None)
        elif op.source == SOURCE_DIGITRAFFIC:
            # The client's records stand in for a feed: parse(records) reads them.
            feed = await self._fetch_digitraffic()
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
            trip_delays = stop_delays(tu, self._static.data, now)
            if self._static.data is not None:
                self._check_timetable(*trip_coverage(tu, self._static.data))
                next_stops = next_stops_from(tu, self._static.data, now)

        extras = None
        if op.parse_stops is not None:
            # Digitraffic: next stops and delays from each train's own timetable.
            next_stops, trip_delays, extras = op.parse_stops(feed, self._static.data, now)

        if self._rail_check is not None:
            self._rail_check.set_shapes(self._static.data)
        if op.source != SOURCE_DIGITRAFFIC and feed.header.HasField("timestamp"):
            self.feed_timestamp = int(feed.header.timestamp)
        # A fix older than the operator's limit is refused before Fleet sees it
        # (poll.fresh_only; SE Queensland's frozen fixes, SSOT 9.1).
        observations, stale = poll.fresh_only(op.parse(feed), now, op.max_fix_age_s)
        result = self.fleet.update(
            observations, now,
            show_parked=self._show_parked, delays=delays, next_stops=next_stops,
            static=self._static.data, trip_delays=trip_delays)
        result["stale"] = stale
        # A fix this old never counts as standing (Finland's tunnel; SSOT 8.1).
        result["unstalled"] = poll.unstall_stale(result, observations, now,
                                                 op.stand_max_fix_age_s)
        poll.apply_extras(result, extras)
        # The operator's own touches after Fleet (SE Queensland: look, label, lateness
        # and the arrow, from the timetable; poll.decorate_all).
        poll.decorate_all(result, observations, self._static.data, op.decorate)
        # Along the tracks from the last fix (D3c-v), after everything that moves or
        # replaces a position.
        if self._track_path is not None:
            result["track_paths"] = poll.add_track_paths(result, self._track_path)
        else:
            # No track network shipped: along each trip's own shape (shapepath; Lee
            # 2026-10-20, "A train cannot exist off of the tracks").
            result["track_paths"] = shapepath.add_shape_paths(result, observations,
                                                              self._static.data)
        if self._push is not None:
            # A train dark in a tunnel is pushed along it on its own stop times, after the
            # paths from the fixes: it replaces the position and the path (D3d, SSOT 8.3).
            names = (self._static.data or {}).get("stops") or {}
            counts = self._push.apply(result, observations, op.tunnel_clocks(feed), now,
                                      names)
            result["estimated"] = counts[tunnel.ESTIMATED]
        self._last_good = result
        return result
