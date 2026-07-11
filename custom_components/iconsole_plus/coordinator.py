"""DataUpdateCoordinator for iConsol+."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.components.bluetooth import async_ble_device_from_address
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from iconsole_plus.client import IConsolePlusClient
from iconsole_plus.models import TelemetryData


_LOGGER = logging.getLogger(__name__)

class IConsolePlusCoordinator(DataUpdateCoordinator[TelemetryData]):
    """Class to manage fetching iConsol+ data."""

    def __init__(self, hass: HomeAssistant, address: str, name: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=None, # We use push updates
        )
        self.address = address
        self.client: IConsolePlusClient | None = None
        self._session_task: asyncio.Task | None = None
        self._current_level: int = 1

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
        """Background task to run the session and push updates."""
        _LOGGER.debug("iConsole+ session task started")
        try:
            async with self.client.session():
                _LOGGER.info("Successfully connected and handshaked with iConsole+ at %s", self.address)
                async for data in self.client:
                    self.async_set_updated_data(data)
        except Exception as err:
            _LOGGER.error("Error in iConsole+ session for %s: %s", self.address, err, exc_info=True)
            self.last_update_success = False
            self.async_update_listeners()
        finally:
            _LOGGER.debug("iConsole+ session task finished, cleaning up")
            self.client = None
            self._session_task = None
            self.async_update_listeners()

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
