"""geo_location entities: one per vehicle on the shared Live Track map.

Contract: 10_SEED/06_MAP_CONTRACT.md section D. Attribute mapping: attributes.py.

* `state` is @final and IS the distance. No distance attribute.
* `state_attributes` is @final (source, latitude, longitude); everything else
  goes in extra_state_attributes or is silently dropped.
* `_attr_source` is the domain, which the shared map filters on.
* ! NO unique_id and NO device_info (D1, 2026-09-23; 05_SHARED_LESSONS.md A9).
  The entity id comes from the name, "<operator> unit <vehicle id>", built
  from the stable vehicle id and never from the label: labels repeat (two
  trains numbered 703 at once; "NIS" on most units).
* An entity is REMOVED when Fleet says the vehicle departed: parked past the
  hold, or absent from the feed past the grace. With no unique_id nothing
  survives the removal and nothing accumulates.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.location import distance as _distance

from .attributes import to_attributes
from .const import DOMAIN
from .coordinator import CommuterRailCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: CommuterRailCoordinator = hass.data[DOMAIN][entry.entry_id]
    live: dict[str, CommuterTrain] = {}

    @callback
    def _sync() -> None:
        data = coordinator.data or {}
        vehicles = data.get("vehicles") or {}
        for gone in data.get("departed") or ():
            entity = live.pop(gone, None)
            if entity is not None:
                entity.async_schedule_removal()
        new = [vid for vid in vehicles if vid not in live]
        if new:
            entities = [CommuterTrain(coordinator, vid) for vid in new]
            live.update(zip(new, entities))
            async_add_entities(entities)

    _sync()
    entry.async_on_unload(coordinator.async_add_listener(_sync))


class CommuterTrain(GeolocationEvent):
    """One commuter rail vehicle."""

    _attr_should_poll = False
    _attr_icon = "mdi:train"
    _attr_unit_of_measurement = "km"
    _attr_source = DOMAIN

    def __init__(self, coordinator: CommuterRailCoordinator, vehicle_id: str) -> None:
        self._coordinator = coordinator
        self._vehicle_id = vehicle_id
        op = coordinator.operator
        self._attr_attribution = op.attribution
        self._attr_name = f"{op.short} unit {vehicle_id}"

    def _rec(self) -> dict[str, Any] | None:
        return ((self._coordinator.data or {}).get("vehicles") or {}).get(self._vehicle_id)

    @callback
    def async_schedule_removal(self) -> None:
        if self.hass is not None:
            self.hass.async_create_task(self.async_remove(force_remove=True))

    @property
    def available(self) -> bool:
        # Missing from one poll is not departed; Fleet waits out a grace.
        return self._coordinator.last_update_success and self._rec() is not None

    @property
    def latitude(self) -> float | None:
        rec = self._rec()
        return rec["latitude"] if rec else None

    @property
    def longitude(self) -> float | None:
        rec = self._rec()
        return rec["longitude"] if rec else None

    @property
    def distance(self) -> float | None:
        """Kilometres from home; the entity's state (@final in the platform)."""
        rec = self._rec()
        if not rec:
            return None
        metres = _distance(self.hass.config.latitude, self.hass.config.longitude,
                           rec["latitude"], rec["longitude"])
        return None if metres is None else metres / 1000

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        rec = self._rec()
        if not rec:
            return {}
        return to_attributes(rec, self._coordinator.operator.id)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state))
