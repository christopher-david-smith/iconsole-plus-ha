"""DataUpdateCoordinator for iConsol+."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.components.bluetooth import async_ble_device_from_address
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from iconsole_plus.client import IConsolePlusClient
from iconsole_plus.models import TelemetryData

_LOGGER = logging.getLogger(__name__)

class IConsolePlusCoordinator(DataUpdateCoordinator[TelemetryData]):
    """Class to manage fetching iConsol+ data."""

    def __init__(self, hass: HomeAssistant, address: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"iConsol+ {address}",
            update_interval=None, # We use push updates
        )
        self.address = address
        self.client: IConsolePlusClient | None = None
        self._session_task: asyncio.Task | None = None
        self._current_level: int = 1

    async def async_start_session(self) -> None:
        """Start the bike session."""
        ble_device = async_ble_device_from_address(self.hass, self.address)
        if not ble_device:
            raise UpdateFailed(f"Could not find device with address {self.address}")

        self.client = IConsolePlusClient(ble_device)
        self._current_level = 1
        self._session_task = self.hass.async_create_task(self._run_session())

    async def _run_session(self) -> None:
        """Background task to run the session and push updates."""
        try:
            async with self.client.session():
                async for data in self.client:
                    self.async_set_updated_data(data)
        except Exception as err:
            _LOGGER.error("Error in iConsol+ session: %s", err)
            self.last_update_success = False
            self.async_update_listeners()
        finally:
            self.client = None
            self._session_task = None

    async def async_stop_session(self) -> None:
        """Stop the bike session."""
        if self._session_task:
            self._session_task.cancel()
            self._session_task = None
