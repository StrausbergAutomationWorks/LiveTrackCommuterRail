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
from saw_livetrack.gtfs import Fleet, decode
from .operators import Operator
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
        self.fleet = Fleet(styling=op.styling)
        self._static = StaticTimetable(hass, self._session, op)
        self._failures = 0
        self._last_good: dict[str, Any] | None = None
        self.feed_timestamp: int | None = None
        self.trip_coverage: tuple[int, int] | None = None
        self._timetable_stale = False

    @property
    def timetable(self) -> dict[str, Any] | None:
        return self._static.info

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

        # The timetable loads and refreshes in the background; until it has,
        # no next station is published and nothing else changes.
        if self._static.due():
            self.config_entry.async_create_background_task(
                self.hass, self._static.async_refresh(), f"{op.id} timetable")

        now = time.time()
        delays = None
        next_stops = None
        trip_delays = None
        if op.trip_updates_url and (op.parse_delays or op.static_url):
            try:
                tu = await fetch_feed(self._session, op.trip_updates_url, self._params)
            except AuthError:
                tu = None
            if tu is not None:
                if op.parse_delays:
                    delays = op.parse_delays(tu)
                # Delay at the next stop, one rule for every feed (backlog 275):
                # the update's own delay, else predicted minus scheduled, which
                # needs the timetable. Fleet prefers it to parse_delays.
                trip_delays = stop_delays(tu, self._static.data, now)
                if self._static.data is not None:
                    self._check_timetable(*trip_coverage(tu, self._static.data))
                    next_stops = next_stops_from(tu, self._static.data, now)

        if feed.header.HasField("timestamp"):
            self.feed_timestamp = int(feed.header.timestamp)
        result = self.fleet.update(
            op.parse(feed), now,
            show_parked=self._show_parked, delays=delays, next_stops=next_stops,
            static=self._static.data, trip_delays=trip_delays)
        self._last_good = result
        return result
