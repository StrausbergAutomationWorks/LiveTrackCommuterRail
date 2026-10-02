"""Two bare count sensors per operator.

! A NUMBER AND NO ATTRIBUTES, deliberately: this install excludes
geo_location from the recorder, so these counts are the only record of the
fleet over time. They are what shows, afterwards, a day like 2026-09-06, when
Metra attributed 13 trains at the morning peak instead of ~85 and a map of
routed trains alone looked like a quiet Sunday (SSOT section 4.4). An
attribute unique on every write would mint a new recorder blob each poll
(05_SHARED_LESSONS.md A7). House pattern: exclude the rich entity, keep a
bare count.

These keep a unique_id and so may carry a device; the per-vehicle entities
may not (05 A9).
"""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import CommuterRailCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: CommuterRailCoordinator = hass.data[DOMAIN][entry.entry_id]
    op = coordinator.operator
    device = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=op.name,
        model="GTFS-Realtime feed",
        entry_type=DeviceEntryType.SERVICE,
    )
    async_add_entities([
        CountSensor(coordinator, entry, device, "trains_in_service",
                    "Trains in service", "trains", "mdi:train"),
        CountSensor(coordinator, entry, device, "non_revenue",
                    "Vehicles not in service", "vehicles", "mdi:train-variant"),
    ])


class CountSensor(SensorEntity):
    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: CommuterRailCoordinator, entry: ConfigEntry,
                 device: DeviceInfo, key: str, name: str, unit: str, icon: str) -> None:
        self._coordinator = coordinator
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_device_info = device
        self._attr_attribution = coordinator.operator.attribution

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success

    @property
    def native_value(self) -> int | None:
        return (self._coordinator.data or {}).get(self._key)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self._coordinator.async_add_listener(self._on_update))

    @callback
    def _on_update(self) -> None:
        self.async_write_ha_state()
