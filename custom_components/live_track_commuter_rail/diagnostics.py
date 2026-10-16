"""Diagnostics download. The key is redacted; nothing else here is secret."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_API_KEY, DOMAIN

TO_REDACT = {CONF_API_KEY}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    data = coordinator.data or {}
    return {
        "entry": {"data": async_redact_data(dict(entry.data), TO_REDACT),
                  "options": dict(entry.options)},
        "operator": coordinator.operator.id,
        "feed_timestamp": coordinator.feed_timestamp,
        "counts": {k: data.get(k) for k in
                   ("trains_in_service", "non_revenue", "vehicles_in_feed", "off_rail", "stale",
                    "track_paths")},
        "track_lines": coordinator.track_lines,
        "published": len(data.get("vehicles") or {}),
        "fleet": coordinator.fleet.stats(),
        "timetable": coordinator.timetable,
        "rail_segments": coordinator.rail_segments,
        "rail_shape_segments": coordinator.rail_shape_segments,
        "trip_coverage": coordinator.trip_coverage,
    }
