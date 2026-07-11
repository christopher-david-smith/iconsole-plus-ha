"""Number platform for iConsol+ resistance."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
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
    """Set up the iConsol+ numbers."""
    coordinator: IConsolePlusCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([IConsolePlusResistanceNumber(coordinator)])

class IConsolePlusResistanceNumber(CoordinatorEntity[IConsolePlusCoordinator], NumberEntity):
    """Number entity to control resistance level."""

    def __init__(self, coordinator: IConsolePlusCoordinator) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_name = "Resistance"
        self._attr_unique_id = f"{coordinator.address}_resistance"
        self._attr_native_min_value = 1
        self._attr_native_max_value = 32
        self._attr_native_step = 1
        self._attr_icon = "mdi:weight-lifter"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> float | None:
        """Return the current resistance level."""
        # Note: We don't have a direct 'level' field in TelemetryData yet, 
        # but the bike sends B6 on change. We should probably track it in the coordinator.
        return getattr(self.coordinator, "_current_level", 1)

    @property
    def available(self) -> bool:
        """The resistance slider is only available during an active session."""
        return self.coordinator.client is not None and self.coordinator.client.is_connected

    async def async_set_native_value(self, value: float) -> None:
        """Set the resistance level."""
        if self.coordinator.client:
            await self.coordinator.client.set_resistance(int(value))
            self.coordinator._current_level = int(value)
            self.async_write_ha_state()
