"""Switch platform for iConsol+."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import IConsolePlusCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the iConsol+ switches."""
    coordinator: IConsolePlusCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([IConsolePlusConnectionSwitch(coordinator)])

class IConsolePlusConnectionSwitch(CoordinatorEntity[IConsolePlusCoordinator], SwitchEntity):
    """Switch to manage the background BLE connection session."""

    def __init__(self, coordinator: IConsolePlusCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_name = "Connection"
        self._attr_unique_id = f"{coordinator.address}_connection"
        self._attr_icon = "mdi:bluetooth"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool:
        """Return true if a connection session is active/enabled."""
        return self.coordinator.client is not None

    @property
    def available(self) -> bool:
        """The connection switch is always available."""
        return True

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable background connection session."""
        await self.coordinator.async_start_session()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable background connection session."""
        await self.coordinator.async_stop_session()
        self.async_write_ha_state()
