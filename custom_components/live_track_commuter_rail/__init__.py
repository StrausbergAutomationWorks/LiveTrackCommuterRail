"""Live Track Commuter Rail for Home Assistant.

Live positions of commuter trains on the shared Live Track map, one config
entry per commuter railroad, each read from that railroad's own
GTFS-Realtime feed. Original work, not affiliated with any operator.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_OPERATOR, DOMAIN
from .coordinator import CommuterRailCoordinator
from .operators import OPERATORS

# ! A new platform needs a FULL Home Assistant restart, not a reload: a reload
# re-runs setup against the modules already imported (06_MAP_CONTRACT.md D6a-0c).
PLATFORMS: list[Platform] = [Platform.GEO_LOCATION, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up one operator."""
    op = OPERATORS[entry.data[CONF_OPERATOR]]
    coordinator = CommuterRailCoordinator(hass, entry, op)
    try:
        await coordinator.async_config_entry_first_refresh()
    except BaseException:
        # A failed setup is retried with a NEW coordinator: give back this one's
        # claim on the shared Digitraffic client, or it would never be released.
        coordinator.release()
        raise
    entry.async_on_unload(coordinator.release)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unloaded


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when options change, so a new interval or filter takes effect."""
    await hass.config_entries.async_reload(entry.entry_id)
