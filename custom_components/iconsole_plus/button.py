"""Button platform for iConsol+."""
from __future__ import annotations

from typing import Any

from homeassistant.components.button import ButtonEntity
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
    """Set up the iConsol+ buttons."""
    coordinator: IConsolePlusCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            IConsolePlusStartWorkoutButton(coordinator),
            IConsolePlusStopWorkoutButton(coordinator),
        ]
    )

class IConsolePlusStartWorkoutButton(CoordinatorEntity[IConsolePlusCoordinator], ButtonEntity):
    """Button to start a workout session on the bike."""

    def __init__(self, coordinator: IConsolePlusCoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_name = "Start Workout"
        self._attr_unique_id = f"{coordinator.address}_start_workout"
        self._attr_icon = "mdi:play"
        self._attr_device_info = coordinator.device_info

    @property
    def available(self) -> bool:
        """Available only when connected to the bike."""
        return self.coordinator.client is not None and self.coordinator.client.is_connected

    async def async_press(self) -> None:
        """Press the button."""
        await self.coordinator.async_start_workout()

class IConsolePlusStopWorkoutButton(CoordinatorEntity[IConsolePlusCoordinator], ButtonEntity):
    """Button to stop/pause a workout session on the bike."""

    def __init__(self, coordinator: IConsolePlusCoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_name = "Stop Workout"
        self._attr_unique_id = f"{coordinator.address}_stop_workout"
        self._attr_icon = "mdi:stop"
        self._attr_device_info = coordinator.device_info

    @property
    def available(self) -> bool:
        """Available only when connected to the bike."""
        return self.coordinator.client is not None and self.coordinator.client.is_connected

    async def async_press(self) -> None:
        """Press the button."""
        await self.coordinator.async_stop_workout()
