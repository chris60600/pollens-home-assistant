"""Config flow for Hello World integration."""
from __future__ import annotations

import logging
from typing import Any
from aiohttp import ClientError

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_RESOURCE
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import aiohttp_client

from .const import (
    CONF_LOCATIONS,
    DOMAIN,
    CONF_COUNTRYCODE,
    CONF_FILTER,
    CONF_SCAN_INTERVAL,
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
    county = client.county_name
    title = f" Pollens {client.county_name}"
    return {"title": title}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hello World."""

    VERSION = 1
    # Pick one of the available connection classes in homeassistant/config_entries.py
    # This tells HA if it should be asking for updates, or it'll be notified of updates
    # automatically. This example uses PUSH, as the dummy hub will notify HA of
    # changes.
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # This goes through the steps to take the user through the setup process.
        # Using this it is possible to update the UI and prompt for additional
        # information. This example provides a single form (built from `DATA_SCHEMA`),
        # and when that has some validated input, it calls `async_create_entry` to
        # actually create the HA config entry. Note the "title" value is returned by
        # `validate_input` above.
        errors = {}
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidCounty:
                errors["base"] = "invalid_county"
                _LOGGER.exception("Invalid county selected")
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_COUNTRYCODE, default=["60"]): vol.In(DEPARTMENTS),
                }
            ),
            description_placeholders={"docs_url": "pollens.fr"},
            errors=errors,
        )

    async def async_step_import(self, conf: dict) -> FlowResult:
        """Import a configuration from config.yaml."""
        return await self.async_step_user(
            user_input={CONF_COUNTRYCODE: conf[CONF_LOCATIONS]}
        )

    def host_already_configured(self, host: str) -> bool:
        """See if we already have a dunehd entry matching user input configured."""
        existing_hosts = {
            entry.data[CONF_COUNTRYCODE] for entry in self._async_current_entries()
        }
        return host in existing_hosts

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlowHandler:
        """Options callback for AccuWeather."""
        return OptionsFlowHandler(config_entry)


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidCounty(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options for AccuWeather."""

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize AccuWeather options flow."""
        self.config_entry = entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(CONF_SCAN_INTERVAL, 60),
                    ): cv.positive_int,
                }
            ),
        )
