"""The iConsol+ integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import IConsolePlusCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.BUTTON,
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up iConsol+ from a config entry."""
    address = entry.data["address"]
    coordinator = IConsolePlusCoordinator(hass, address, entry.title, entry)
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register options update listener
    entry.async_on_unload(entry.add_update_listener(update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    coordinator: IConsolePlusCoordinator = hass.data[DOMAIN][entry.entry_id]
    coordinator.use_custom_calories = entry.options.get("calculate_calories", False)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: IConsolePlusCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_stop_session()

    return unload_ok
