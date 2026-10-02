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
from google.transit import gtfs_realtime_pb2

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
from .fleet import Fleet
from .operators import Operator

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
    try:
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(raw)
    except Exception as err:  # noqa: BLE001 - a bad payload, whatever its shape
        _LOGGER.debug("feed decode failed: %s", type(err).__name__)
        return None
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
        self._failures = 0
        self._last_good: dict[str, Any] | None = None
        self.feed_timestamp: int | None = None

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

        delays = None
        if op.trip_updates_url and op.parse_delays:
            try:
                tu = await fetch_feed(self._session, op.trip_updates_url, self._params)
            except AuthError:
                tu = None
            if tu is not None:
                delays = op.parse_delays(tu)

        if feed.header.HasField("timestamp"):
            self.feed_timestamp = int(feed.header.timestamp)
        result = self.fleet.update(
            op.parse(feed), time.time(),
            show_parked=self._show_parked, delays=delays)
        self._last_good = result
        return result
