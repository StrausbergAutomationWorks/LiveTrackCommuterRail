"""The operator's GTFS static timetable, distilled and cached on disk.

STORAGE. JSON at .storage/saw_gtfs_<operator id>.json - the shared-file naming
convention (project instructions: caches of public datasets are named after
the DATASET, never after an integration), so anything else that needs the
same railroad's timetable finds it.

Refreshed once a day; a failed refresh keeps the last good copy and is not
retried for an hour. Without any copy, no next station is published and
nothing else changes: positions never wait for this.

! NO KEY GOES HERE. Both timetables are public; the realtime key belongs to
the realtime feed only and is never sent to another host.
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant

from .const import USER_AGENT
from .operators import Operator
from saw_livetrack.gtfs import STATIC_VERSION, distill

_LOGGER = logging.getLogger(__name__)

REFRESH_S = 24 * 3600
RETRY_S = 3600
FETCH_TIMEOUT = 60
MAX_BYTES = 20 * 1024 * 1024


class StaticTimetable:
    """One operator's distilled timetable, loaded lazily, refreshed daily."""

    def __init__(self, hass: HomeAssistant, session: aiohttp.ClientSession,
                 op: Operator) -> None:
        self._hass, self._session, self._op = hass, session, op
        self._path = hass.config.path(".storage", f"saw_gtfs_{op.id}.json")
        self._data: dict[str, Any] | None = None
        self._loaded = False
        self._busy = False
        self._next_try = 0.0

    @property
    def data(self) -> dict[str, Any] | None:
        return self._data

    def due(self) -> bool:
        """Worth calling async_ensure: never loaded, stale, and not in a retry wait."""
        if not self._op.static_url or self._busy:
            return False
        if not self._loaded:
            return True
        now = time.time()
        fresh = self._data is not None and now - float(self._data.get("fetched_at", 0)) < REFRESH_S
        return not fresh and now >= self._next_try

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
        return d if isinstance(d, dict) and d.get("v") == STATIC_VERSION else None

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
        if fresh or now < self._next_try:
            return self._data
        self._next_try = now + RETRY_S
        try:
            async with self._session.get(
                op.static_url, headers={"User-Agent": USER_AGENT},
                timeout=aiohttp.ClientTimeout(total=FETCH_TIMEOUT),
            ) as resp:
                if resp.status != 200:
                    _LOGGER.debug("%s timetable answered HTTP %s", op.id, resp.status)
                    return self._data
                if (resp.content_length or 0) > MAX_BYTES:
                    _LOGGER.debug("%s timetable larger than %s bytes; ignored", op.id, MAX_BYTES)
                    return self._data
                raw = await resp.read()
            if len(raw) > MAX_BYTES:
                _LOGGER.debug("%s timetable larger than %s bytes; ignored", op.id, MAX_BYTES)
                return self._data
            d = await self._hass.async_add_executor_job(
                lambda: distill(raw, stop_times=op.static_stop_times))
            d["fetched_at"] = now
            d["source"] = op.static_url
            await self._hass.async_add_executor_job(self._write, d)
        except Exception as err:  # noqa: BLE001 - a timetable never stops the map
            _LOGGER.debug("%s timetable refresh failed: %s", op.id, type(err).__name__)
            return self._data
        self._data = d
        _LOGGER.debug("%s timetable refreshed: %s stops", op.id, len(d.get("stops", {})))
        return self._data
