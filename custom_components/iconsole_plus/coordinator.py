"""DataUpdateCoordinator for iConsol+."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.components.bluetooth import async_ble_device_from_address
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from dataclasses import replace as dataclass_replace

from .const import DOMAIN
from iconsole_plus.client import IConsolePlusClient
from iconsole_plus.models import TelemetryData


_LOGGER = logging.getLogger(__name__)

class IConsolePlusCoordinator(DataUpdateCoordinator[TelemetryData]):
    """Class to manage fetching iConsol+ data."""

    def __init__(self, hass: HomeAssistant, address: str, name: str, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=None, # We use push updates
        )
        self.address = address
        self.entry = entry
        self.client: IConsolePlusClient | None = None
        self._session_task: asyncio.Task | None = None
        self._current_level: int = 1
        self.use_custom_calories: bool = entry.options.get("calculate_calories", False)

        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, address)},
            name=name,
            manufacturer="iConsole+",
            model="Fitness Equipment",
        )

    async def async_start_session(self) -> None:
        """Start the bike session."""
        if self._session_task is not None:
            _LOGGER.debug("iConsole+ session already starting or active for %s", self.address)
            return

        _LOGGER.debug("Starting iConsole+ session for %s", self.address)
        ble_device = async_ble_device_from_address(self.hass, self.address)
        if not ble_device:
            _LOGGER.warning("Device %s not found in Bluetooth cache, will attempt to find it during connection", self.address)
            # Use the address string as fallback
            device_to_use = self.address
        else:
            device_to_use = ble_device

        self.client = IConsolePlusClient(device_to_use)
        self._current_level = 1
        self._session_task = self.hass.async_create_task(self._run_session())

    async def _run_session(self) -> None:
        """Background task to run the session and push updates with auto-reconnect."""
        _LOGGER.debug("iConsole+ session task started")
        last_update_time = None
        cumulative_calories = 0.0

        while True:
            try:
                async with self.client.session():
                    _LOGGER.info("Successfully connected and handshaked with iConsole+ at %s", self.address)
                    async for data in self.client:
                        current_time = asyncio.get_running_loop().time()
                        if last_update_time is not None:
                            dt = current_time - last_update_time
                            if 0 < dt < 5.0:
                                # Joules = Watts * seconds
                                work_joules = data.power_watts * dt
                                # Convert to kcal (assuming 22% biological efficiency)
                                # kcal = Joules / (4184 * 0.22)
                                cumulative_calories += work_joules / 920.48
                        last_update_time = current_time

                        if self.use_custom_calories:
                            data = dataclass_replace(data, calories_kcal=round(cumulative_calories))

                        self.async_set_updated_data(data)
            except asyncio.CancelledError:
                _LOGGER.debug("Session task cancelled, stopping reconnect loop")
                raise
            except Exception as err:
                _LOGGER.warning("Error in iConsole+ session, will attempt reconnect in 10s: %s", err, exc_info=True)
                self.last_update_success = False
                self.async_update_listeners()
                await asyncio.sleep(10.0)

    async def async_stop_session(self) -> None:
        """Stop the bike session."""
        if self._session_task:
            _LOGGER.debug("Stopping iConsole+ session for %s", self.address)
            task = self._session_task
            self._session_task = None
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def async_start_workout(self) -> None:
        """Start the workout."""
        if self.client:
            _LOGGER.info("Sending start workout command")
            await self.client.start_workout()

    async def async_stop_workout(self) -> None:
        """Stop the workout."""
        if self.client:
            _LOGGER.info("Sending stop workout command")
            await self.client.stop_workout()
