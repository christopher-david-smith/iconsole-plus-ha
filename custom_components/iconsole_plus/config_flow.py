"""Config flow for iConsol+ integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for iConsol+."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle bluetooth discovery."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        
        self._discovery_info = discovery_info
        self.context["title_placeholders"] = {"name": discovery_info.name}
        return await self.async_step_user()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title=self._discovery_info.name if self._discovery_info else "iConsol+",
                data={
                    "address": self._discovery_info.address if self._discovery_info else user_input["address"],
                },
            )

        if self._discovery_info:
            return self.async_show_form(
                step_id="user",
                description_placeholders={"name": self._discovery_info.name},
            )

        # List discovered devices
        discovered = async_discovered_service_info(self.hass)
        device_options = {
            service.address: f"{service.name or 'Unknown'} ({service.address})"
            for service in discovered
            if any(uuid.lower() == "49535343-fe7d-4ae5-8fa9-9fafd205e455" for uuid in service.service_uuids)
            or "iconsole" in (service.name or "").lower()
        }

        # If no devices found with the specific UUID, wait a few seconds and try once more
        # This gives the HA bluetooth scanner a chance to populate if it was idle
        if not device_options and not self.context.get("tried_scan"):
            self.context["tried_scan"] = True
            await asyncio.sleep(5.0)
            return await self.async_step_user()

        # If still no devices found, show a text input for manual address
        if not device_options:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required("address"): str,
                    }
                ),
                description_placeholders={"name": "iConsole+"},
                errors={"base": "no_devices_found_manual"},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("address"): vol.In(device_options),
                }
            ),
        )
