"""Config flow for Pollens integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant import config_entries, exceptions
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers import selector

from .const import (
    CONF_VERSION,
    DOMAIN,
    KEY_TO_ATTR,
    CONF_COUNTRYCODE,
    CONF_SCAN_INTERVAL,
    CONF_POLLENSLIST,
    CONF_LITERAL,
)
from .dept import DEPARTMENTS

from .pollensasync import PollensClient

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    # Validate the data can be used to set up a connection.
    if len(data[CONF_COUNTRYCODE]) != 2:
        raise InvalidCounty

    session = aiohttp_client.async_get_clientsession(hass)
    client = PollensClient(session)
    result = await client.Get(data[CONF_COUNTRYCODE])
    if not result:
        # If there is an error, raise an exception to notify HA that there was a
        # problem. The UI will also show there was a problem
        raise CannotConnect
    title = f"Pollens {client.county_name}"
    return {"title": title}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pollens."""

    VERSION = CONF_VERSION
    # Pick one of the available connection classes in homeassistant/config_entries.py
    # This tells HA if it should be asking for updates, or it'll be notified of updates
    # automatically. This example uses PUSH, as the dummy hub will notify HA of
    # changes.
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize"""
        self.data = None
        self._init_info = {}

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                self._init_info["data"] = user_input
                self._init_info["info"] = await validate_input(self.hass, user_input)
                return await self.async_step_select_pollens()
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidCounty:
                errors["base"] = "invalid_county"
                _LOGGER.exception("Invalid county selected")
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        entries = self._async_current_entries()
        # Remove county from the list (already configured)
        for entry in entries:
            if entry.data[CONF_COUNTRYCODE] in DEPARTMENTS:
                DEPARTMENTS.pop(entry.data[CONF_COUNTRYCODE])

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_COUNTRYCODE, default=["60"]): vol.In(DEPARTMENTS),
                    vol.Required(CONF_LITERAL, default=True): cv.boolean,
                }
            ),
            description_placeholders={"docs_url": "pollens.fr"},
            errors=errors,
        )

    async def async_step_select_pollens(self, user_input=None):
        """Select pollens step 2"""
        if user_input is not None:
            _LOGGER.info("Select pollens step")
            self._init_info["data"][CONF_POLLENSLIST] = user_input[CONF_POLLENSLIST]
            return self.async_create_entry(
                title=self._init_info["info"]["title"], data=self._init_info["data"]
            )
        pollens = [pollen for pollen in KEY_TO_ATTR]
        return self.async_show_form(
            step_id="select_pollens",
            data_schema=vol.Schema(
                {vol.Optional(CONF_POLLENSLIST): cv.multi_select(pollens)}
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlowHandler:
        """Options callback for Pollens."""
        return OptionsFlowHandler(config_entry)


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidCounty(exceptions.HomeAssistantError):
    """Error to invalid county."""


class InvalidScanInterval(exceptions.HomeAssistantError):
    """Error to invalid scan interval ."""


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options for Pollens."""

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize Pollens options flow."""
        self.config_entry = entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        _LOGGER.info("Changing options of pollens integration")
        errors = {}
        if user_input is not None:
            # Validate the data can be used to set up a connection.
            _LOGGER.info(
                "Change option of %s to %s",
                self.config_entry.title,
                user_input[CONF_SCAN_INTERVAL],
            )
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    # Configuration of scan interval mini 3 h max 24h              
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(CONF_SCAN_INTERVAL, 1),
                    ): selector.NumberSelector(selector.NumberSelectorConfig(min=3, max=24, mode=selector.NumberSelectorMode.BOX)),
                }
            ),
            errors=errors,
        )
