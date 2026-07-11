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
    async_add_entities([IConsolePlusWorkoutSwitch(coordinator)])

class IConsolePlusWorkoutSwitch(CoordinatorEntity[IConsolePlusCoordinator], SwitchEntity):
    """Switch to start/stop a workout session."""

    def __init__(self, coordinator: IConsolePlusCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_name = "Workout"
        self._attr_unique_id = f"{coordinator.address}_workout"
        self._attr_icon = "mdi:bike"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool:
        """Return true if a session is active."""
        return self.coordinator.client is not None and self.coordinator.client.is_connected

    @property
    def available(self) -> bool:
        """The workout switch is always available to allow starting a session."""
        return True

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Start the workout session."""
        await self.coordinator.async_start_session()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Stop the workout session."""
        await self.coordinator.async_stop_session()
        self.async_write_ha_state()
