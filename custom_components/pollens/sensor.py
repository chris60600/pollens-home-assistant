"""Support for the RNSA pollens service."""
import asyncio
from datetime import timedelta
import logging
import json
from os import name
import sys
import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components import sensor
from homeassistant.config_entries import ConfigEntry, SOURCE_IMPORT
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from homeassistant.core import HomeAssistant
from .pollensasync import PollensClient

from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_SCAN_INTERVAL,
)
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

import homeassistant.components.time_date.sensor as time_date
from .const import (
    DOMAIN,
    LIST_RISK,
    ATTR_URL,
    ATTR_COUNTY_NAME,
    KEY_TO_ATTR,
    ATTRIBUTION,
    COORDINATOR,
    CONF_COUNTRYCODE,
    CONF_LOCATIONS,
    CONF_FILTER,
    CONF_TIMEOUT,
    CONF_SCANINTERVAL,
)
from . import PollensClient, PollensEntity, PollensUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

ICONS = {
    0: "mdi:check",
    1: "mdi:check",
    2: "mdi:alert-outline",
    3: "mdi:alert-outline",
    4: "mdi:alert",
    5: "mdi:alert",
}


SCAN_INTERVAL = timedelta(minutes=30)
TIMEOUT = 30

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_LOCATIONS): cv.string,
        vol.Optional(CONF_TIMEOUT, default=TIMEOUT): cv.positive_int,
        vol.Optional(CONF_SCANINTERVAL, default=SCAN_INTERVAL): cv.time_period,
        vol.Optional(CONF_FILTER, default=0): cv.positive_int,
    }
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup Sensor Plateform"""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    # api: PollensClient = hass.data[DOMAIN][entry.entry_id]["pollens_api"]
    sensors = []
    # await api.Get("60")
    for risk in coordinator.api.risks:
        name = risk
        icon = KEY_TO_ATTR[risk.lower()][1]
        sensors.append(PollenSensor(coordinator, name=name, icon=icon, entry=entry))

    name = f"pollens_{coordinator.county}"
    icon = ICONS[0]
    sensors.append(
        RiskSensor(coordinator=coordinator, name=name, icon=icon, entry=entry)
    )

    async_add_entities(sensors, True)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: None,
) -> None:
    """Set up the requested Pollens location."""
    _LOGGER.warning(
        "Loading Pollens via platform setup is deprecated. Please remove it from your yaml configuration"
    )

    # try:
    #     county_number = config.pop(CONF_LOCATIONS)
    #     pollens_filter = config.pop(CONF_FILTER)
    #     timeout = config.pop(CONF_TIMEOUT)
    #     scan_interval = config.pop(CONF_SCANINTERVAL)
    # except KeyError:
    #     pass

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data=config,
        )
    )


class PollenSensor(PollensEntity, SensorEntity):
    """ """

    def __init__(
        self,
        coordinator: PollensUpdateCoordinator,
        name: str,
        icon: str,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, name, icon, entry)
        self._name = f"pollens_{coordinator.county}_{KEY_TO_ATTR[name.lower()][0]}"
        self._state = coordinator.api.risks[name]
        self._unique_id = f"{entry.entry_id}_{self._name}"
        self._attr_name = name
        self._attr_unique_id = self._unique_id

        self._attr_icon = icon

    @property
    def name(self):
        return self._name

    @property
    def native_value(self):
        value = self.coordinator.api.risks[self._attr_name]
        return LIST_RISK[value]

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id


class RiskSensor(PollensEntity, SensorEntity):
    """"""

    def __init__(
        self,
        coordinator: PollensUpdateCoordinator,
        name: str,
        icon: str,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, name, icon, entry)
        self._risk_level = coordinator.api.risk_level
        self._attr_unique_id = f"{entry.entry_id}_{coordinator.county}"
        self._attr_icon = icon
        self._name = name

    @property
    def native_value(self):
        value = self.coordinator.api.risk_level
        return LIST_RISK[value]

    @property
    def icon(self):
        return ICONS[self._risk_level]

    @property
    def name(self):
        return self._name

    @property
    def extra_state_attributes(self):
        attrs = {}
        attrs[ATTR_URL] = "https://pollens.fr"
        attrs[ATTR_COUNTY_NAME] = self.coordinator.api.county_name
        return attrs


class PollensSensor(PollensEntity, SensorEntity):
    """Implementation of a WAQI sensor."""

    def __init__(self, client, county_number, county_name, pollens_filter):
        """Initialize the sensor."""
        self._client = client

        try:
            self.county_name = county_name
            self.county_number = county_number
            self.filter = pollens_filter
            _LOGGER.info(
                "Init pollens sensor for %s county (level=%d)",
                self.county_name,
                self.filter,
            )
        except (KeyError, TypeError):
            self.county_name = None
            self.county_number = None

        self._data = None

    @property
    def name(self):
        """Return the name of the sensor."""
        if self.county_name:
            return f"pollens {self.county_name}"
        return f"pollens {self.county_number}"

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        if self._data is not None:
            return ICONS[self._data.get("riskLevel")]
        return ICONS[0]

    @property
    def state(self):
        """Return the state of the device."""
        if self._data is not None:
            _LOGGER.debug("%s: Update pollens state", self.name)
            return LIST_RISK[self._data.get("riskLevel")]
        return None

    @property
    def available(self):
        """Return sensor availability."""
        return self._data is not None

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the last update."""
        attrs = {}

        if self._data is not None:
            try:
                _LOGGER.debug("%s: Update attributes", self.name)
                attrs[ATTR_ATTRIBUTION] = ATTRIBUTION
                attrs[ATTR_URL] = "https://pollens.fr"
                attrs[ATTR_COUNTY_NAME] = self.county_name

                risks = [
                    item for item in self._data["risks"] if item["level"] >= self.filter
                ]
                _LOGGER.info("%d risque(s) superieur à %d", len(risks), self.filter)
                for risk in risks:
                    _LOGGER.info("- Risque %s : %d", risk["pollenName"], risk["level"])
                    attrs[KEY_TO_ATTR[risk["pollenName"].lower()]] = LIST_RISK[
                        risk["level"]
                    ]
                return attrs
            except (IndexError, KeyError) as err:
                _LOGGER.warning(
                    "%s: Attribution exception %s", self.name, "error {}".format(err)
                )
                return {ATTR_ATTRIBUTION: ATTRIBUTION}

    async def async_update(self):
        """Get the latest data and updates the states and attributes."""
        if self.county_number:
            _LOGGER.debug(
                "%s: Updating sensor pollens for %s", self.name, self.county_name
            )
            result = json.loads(await self._client.Get(number=self.county_number))
            _LOGGER.debug(
                "%s: Pollens sensor updated. receive %d",
                self.name,
                sys.getsizeof(result),
            )
        else:
            result = None
        self._data = result
