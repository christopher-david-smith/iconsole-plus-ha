"""Sensor platform for iConsol+."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfSpeed,
    UnitOfPower,
    UnitOfLength,
    UnitOfEnergy,
    UnitOfTime,
)
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
    """Set up the iConsol+ sensors."""
    coordinator: IConsolePlusCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            IConsolePlusSensor(coordinator, "speed", "Speed", UnitOfSpeed.KILOMETERS_PER_HOUR, SensorDeviceClass.SPEED),
            IConsolePlusSensor(coordinator, "cadence", "Cadence", "RPM", None),
            IConsolePlusSensor(coordinator, "power", "Power", UnitOfPower.WATT, SensorDeviceClass.POWER),
            IConsolePlusSensor(coordinator, "distance", "Distance", UnitOfLength.KILOMETERS, SensorDeviceClass.DISTANCE),
            IConsolePlusSensor(coordinator, "calories", "Calories", UnitOfEnergy.KILO_CALORIE, None),
            IConsolePlusSensor(coordinator, "duration", "Duration", UnitOfTime.SECONDS, SensorDeviceClass.DURATION),
            IConsolePlusSensor(coordinator, "heart_rate", "Heart Rate", "bpm", None),
        ]
    )

class IConsolePlusSensor(CoordinatorEntity[IConsolePlusCoordinator], SensorEntity):
    """Representation of an iConsol+ sensor."""

    def __init__(
        self,
        coordinator: IConsolePlusCoordinator,
        key: str,
        name: str,
        unit: str | None,
        device_class: SensorDeviceClass | None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"{coordinator.name} {name}"
        self._attr_unique_id = f"{coordinator.address}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | int | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        if self._key == "speed":
            return self.coordinator.data.speed_kmh
        if self._key == "cadence":
            return self.coordinator.data.cadence_rpm
        if self._key == "power":
            return self.coordinator.data.power_watts
        if self._key == "distance":
            return self.coordinator.data.distance_km
        if self._key == "calories":
            return self.coordinator.data.calories_kcal
        if self._key == "duration":
            return self.coordinator.data.duration_seconds
        if self._key == "heart_rate":
            return self.coordinator.data.heart_rate_bpm
        return None
