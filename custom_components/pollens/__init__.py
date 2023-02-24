"""Pollens Allergy component."""
from __future__ import annotations
from datetime import timedelta
import logging
from os import error
from re import I
from typing import Any

from aiohttp.client_exceptions import ClientError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL, CONF_SENSORS, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
    UpdateFailed,
)

from .const import (
    ATTRIBUTION,
    CONF_LITERAL,
    CONF_POLLENSLIST,
    CONF_VERSION,
    DOMAIN,
    COORDINATOR,
    UNDO_LISTENER,
    CONF_COUNTRYCODE,
    CONF_SCAN_INTERVAL,
    KEY_TO_ATTR,
)

from .pollensasync import PollensClient

# List of platforms to support. There should be a matching .py file for each,
# eg <cover.py> and <sensor.py>
PLATFORMS: list[str] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up pollens integation"""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up pollens from a config entry."""

    conf = entry.data

    session = aiohttp_client.async_get_clientsession(hass)
    api = PollensClient(session)

    county = conf[CONF_COUNTRYCODE]
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, 3)

    await api.Get(county)

    name = f"Pollens {api.county_name}"

    coordinator = PollensUpdateCoordinator(
        hass=hass,
        name=name,
        scan_interval=scan_interval,
        county=county,
        api=api,
    )

    await coordinator.async_config_entry_first_refresh()

    # Add and update listener
    undo_listener = entry.add_update_listener(_async_update_listener)

    # Setup coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        COORDINATOR: coordinator,
        UNDO_LISTENER: undo_listener,
        "pollens_api": api,
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.debug("Setup of %s successful", entry.title)

    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate the config entry upon new versions."""
    version = entry.version
    data = {**entry.data}

    _LOGGER.debug("Migrating from version %s", version)

    # 1 -> 2: Remove unused condition data:
    if version == 1:
        data.pop(CONF_SENSORS, None)
        data[CONF_POLLENSLIST] = [pollen for pollen in KEY_TO_ATTR]
        data[CONF_LITERAL] = True
        version = entry.version = CONF_VERSION
        hass.config_entries.async_update_entry(entry, data=data)
        _LOGGER.debug("Migration to version %s successful", version)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Update when config_entry options update"""
    await hass.config_entries.async_reload(entry.entry_id)


class PollensUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Pollens data API"""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        scan_interval: int,
        api: str,
        county: str,
        # level_filter: int,
    ) -> None:

        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=name,
            update_interval=timedelta(hours=scan_interval),
        )

        self.api = api
        self.name = name
        self.county = county

    async def _async_update_data(self):
        _LOGGER.info("Update data from web site for %s", self.name)
        try:
            return await self.api.Get(self.county)
        except ClientError as error:
            raise UpdateFailed(f"Error updating from RSSA : {error}") from error


class PollensEntity(CoordinatorEntity):
    """Implementation of the base pollens Entity"""

    _attr_extra_state_attributes = {"attribution": ATTRIBUTION}

    def __init__(
        self,
        coordinator: PollensUpdateCoordinator,
        name: str,
        icon: str,
        entry: ConfigEntry,
    ) -> None:
        """Initialize"""

        super().__init__(coordinator=coordinator)

        # self._attr_unique_id = f"{entry.entry_id}_{KEY_TO_ATTR[name.lower()][0]}"
        # self._attr_icon = icon
        # self._unique_id = f"pollens_{entry.entry_id}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={
                (
                    DOMAIN,
                    str(
                        f"{self.platform.config_entry.unique_id}{self.platform.config_entry.data['county']}"
                    ),
                )
            },
            manufacturer="RNSA",
            model="Pollens sensor",
            name=self.coordinator.name,
        )
