"""The operator's GTFS static timetable, distilled and cached on disk.

STORAGE. JSON at .storage/saw_gtfs_<operator id>.json - the shared-file naming
convention (project instructions: caches of public datasets are named after
the DATASET, never after an integration), so anything else that needs the
same railroad's timetable finds it.

Refreshed once a day; a failed refresh keeps the last good copy and is not
retried for an hour. Refreshed EARLY when the coordinator finds the realtime feed's trips
missing from it (request_refresh; Metra's 2026 GTFS static change renames every
trip), still no more than once an hour. Without any copy, no next station is published and
nothing else changes: positions never wait for this.

! NO KEY GOES HERE. Both timetables are public; the realtime key belongs to
the realtime feed only and is never sent to another host.
"""

from __future__ import annotations

import io
import json
import logging
import os
import time
import zipfile
from typing import Any, Callable

import aiohttp

from homeassistant.core import HomeAssistant

from .const import USER_AGENT
from . import gtfs_filter, rail
from .operators import Operator
from saw_livetrack.gtfs import STATIC_VERSION, distill

_LOGGER = logging.getLogger(__name__)

REFRESH_S = 24 * 3600
RETRY_S = 3600
# A timetable from a shared client that has not loaded its copy yet: asked again soon.
SOURCE_WAIT_S = 60


def _distill(raw: bytes, op: Operator) -> dict[str, Any]:
    """distill, plus the railroad's own route lines for the off-rail check
    (rail.RailCheck, SSOT 7.10) and the operator's extras (SSOT 9). A railroad whose zip
    carries other modes is cut to its own route_types first (gtfs_filter)."""
    if op.static_window:
        # Renfe (SSOT 10): the season's timetable cut to the days around today and the
        # operator's own network first. MEASURED on the laptop: cut by route_type alone
        # it took 66 s and peaked at 930 MB; cut to the window 27 s and 104 MB.
        raw = gtfs_filter.keep_service_window(raw, op.static_route_types,
                                              route_prefixes=op.static_route_prefixes)
    elif op.static_route_types:
        raw = gtfs_filter.keep_route_types(raw, op.static_route_types)
    d = distill(raw, stop_times=op.static_stop_times)
    d["rail_shapes"], index = rail.shapes_indexed(raw)
    if op.static_extras is not None:
        d["extras"] = op.static_extras(zipfile.ZipFile(io.BytesIO(raw)), d, index)
    return d


class StaticTimetable:
    """One operator's distilled timetable, loaded lazily, refreshed daily."""

    def __init__(self, hass: HomeAssistant, session: aiohttp.ClientSession,
                 op: Operator, raw_source: Callable[[], bytes | None] | None = None) -> None:
        self._hass, self._session, self._op = hass, session, op
        # A shared client that already downloads this zip (Renfe): the bytes come from
        # it, never a second download (blocking; None until it has them).
        self._raw_source = raw_source
        self._path = hass.config.path(".storage", f"saw_gtfs_{op.id}.json")
        self._data: dict[str, Any] | None = None
        self._loaded = False
        self._busy = False
        self._next_try = 0.0
        self._forced = False   # an early refresh was asked for

    @property
    def data(self) -> dict[str, Any] | None:
        return self._data

    @property
    def info(self) -> dict[str, Any] | None:
        """Which timetable is cached, for diagnostics."""
        d = self._data
        if d is None:
            return None
        return {k: d.get(k) for k in ("feed_version", "feed_start", "feed_end", "fetched_at")} | {
            "trips_scheduled": len(d.get("sched") or {})}

    def due(self) -> bool:
        """Worth calling async_ensure: never loaded, stale, and not in a retry wait."""
        if not self._op.static_url or self._busy:
            return False
        if not self._loaded:
            return True
        now = time.time()
        if self._forced and now >= self._next_try:
            return True
        fresh = self._data is not None and now - float(self._data.get("fetched_at", 0)) < REFRESH_S
        return not fresh and now >= self._next_try

    def request_refresh(self) -> None:
        """Refresh before the day is out: the realtime feed's trips are not in
        this timetable (coordinator, trip_coverage). Still at most once per
        RETRY_S, so a cutover the two feeds make hours apart costs one
        download an hour, not one a poll."""
        self._forced = True

    async def async_refresh(self) -> None:
        """async_ensure as a background job: positions never wait for it."""
        if self._busy:
            return
        self._busy = True
        try:
            await self.async_ensure()
        finally:
            self._busy = False

    def _read(self) -> dict[str, Any] | None:
        try:
            with open(self._path, encoding="utf-8") as fh:
                d = json.load(fh)
        except (OSError, ValueError):
            return None
        # A cache from before 2026-10-09 has no rail_shapes: fetched again, once.
        # An operator with extras needs them too (SE Queensland's look and arrow).
        return (d if isinstance(d, dict) and d.get("v") == STATIC_VERSION and "rail_shapes" in d
                and (self._op.static_extras is None or "extras" in d)
                else None)

    def _write(self, d: dict[str, Any]) -> None:
        tmp = self._path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, separators=(",", ":"))
        os.replace(tmp, self._path)

    async def async_ensure(self) -> dict[str, Any] | None:
        """The timetable, refreshing it first when it is due. Never raises."""
        op = self._op
        if not op.static_url:
            return None
        if not self._loaded:
            self._loaded = True
            self._data = await self._hass.async_add_executor_job(self._read)
        now = time.time()
        fresh = self._data is not None and now - float(self._data.get("fetched_at", 0)) < REFRESH_S
        if (fresh and not self._forced) or now < self._next_try:
            return self._data
        self._forced = False
        self._next_try = now + RETRY_S
        if self._raw_source is not None:
            return await self._async_from_source(now)
        try:
            async with self._session.get(
                op.static_url, headers={"User-Agent": USER_AGENT, **(op.static_headers or {})},
                timeout=aiohttp.ClientTimeout(total=op.static_timeout_s),
            ) as resp:
                if resp.status != 200:
                    _LOGGER.debug("%s timetable answered HTTP %s", op.id, resp.status)
                    return self._data
                if (resp.content_length or 0) > op.static_max_bytes:
                    _LOGGER.debug("%s timetable larger than %s bytes; ignored", op.id,
                                  op.static_max_bytes)
                    return self._data
                raw = await resp.read()
            if len(raw) > op.static_max_bytes:
                _LOGGER.debug("%s timetable larger than %s bytes; ignored", op.id,
                              op.static_max_bytes)
                return self._data
            d = await self._hass.async_add_executor_job(
                lambda: _distill(raw, op))
            d["fetched_at"] = now
            d["source"] = op.static_url
            await self._hass.async_add_executor_job(self._write, d)
        except Exception as err:  # noqa: BLE001 - a timetable never stops the map
            _LOGGER.debug("%s timetable refresh failed: %s", op.id, type(err).__name__)
            return self._data
        self._data = d
        _LOGGER.debug("%s timetable refreshed: %s stops, %s trips scheduled, feed_version %s",
                      op.id, len(d.get("stops", {})), len(d.get("sched", {})), d.get("feed_version"))
        return self._data

    async def _async_from_source(self, now: float) -> dict[str, Any] | None:
        """The refresh from the shared client's copy of the zip. Never raises."""
        op = self._op
        try:
            raw = await self._hass.async_add_executor_job(self._raw_source)
            if raw is None:
                # The client is still downloading it (36 s for Renfe's): soon, not in an hour.
                self._next_try = now + SOURCE_WAIT_S
                return self._data
            d = await self._hass.async_add_executor_job(lambda: _distill(raw, op))
            d["fetched_at"] = now
            d["source"] = op.static_url
            await self._hass.async_add_executor_job(self._write, d)
        except Exception as err:  # noqa: BLE001 - a timetable never stops the map
            _LOGGER.debug("%s timetable refresh failed: %s", op.id, type(err).__name__)
            return self._data
        self._data = d
        _LOGGER.debug("%s timetable distilled from the shared client: %s trips scheduled",
                      op.id, len(d.get("sched", {})))
        return self._data
