"""Support for the RNSA pollens service."""
import asyncio
from datetime import timedelta
import logging
import json
import sys
import aiohttp
import voluptuous as vol
from .pollensasync import PollensClient

from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_SCAN_INTERVAL,
)
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
import homeassistant.components.time_date.sensor as time_date

_LOGGER = logging.getLogger(__name__)

ATTR_TILLEUL = "tilleul"
ATTR_AMBROISIES = "ambroisies"
ATTR_OLIVIER = "olivier"
ATTR_PLANTAIN = "plantain"
ATTR_NOISETIER= "noisetier"
ATTR_AULNE = "aulne"
ATTR_ARMOISE = "armoise"
ATTR_CHATAIGNIER = "chataignier"
ATTR_URTICACEES = "urticacees"
ATTR_OSEILLE = "oseille"
ATTR_GRAMINEES = "graminees"
ATTR_CHENE = "chene"
ATTR_PLATANE = "platane"
ATTR_BOULEAU = "bouleau"
ATTR_CHARME = "charme"
ATTR_PEUPLIER = "peuplier"
ATTR_FRENE = "frene"
ATTR_SAULE = "saule"
ATTR_CYPRES = "cypres"
ATTR_CUPRESSASEES = "cupressacees"

ATTR_COUNTY_NAME = "departement"
ATTR_URL = "url"

KEY_TO_ATTR = {
    "tilleul":ATTR_TILLEUL,
    "ambroisies": ATTR_AMBROISIES, 
    "olivier": ATTR_OLIVIER,
    "plantain": ATTR_PLANTAIN,
    "noisetier": ATTR_NOISETIER,
    "aulne": ATTR_AULNE,
    "armoise": ATTR_ARMOISE,
    "châtaignier": ATTR_CHATAIGNIER,
    "urticacées": ATTR_URTICACEES,
    "oseille": ATTR_OSEILLE,
    "graminées": ATTR_GRAMINEES,
    "chêne": ATTR_CHENE,
    "platane": ATTR_PLATANE,
    "bouleau": ATTR_BOULEAU,
    "charme": ATTR_CHARME,
    "peuplier": ATTR_PEUPLIER,
    "frêne": ATTR_FRENE,
    "saule": ATTR_SAULE,
    "cyprès": ATTR_CYPRES,
    "cupressacées": ATTR_CUPRESSASEES,
}

LIST_RISK = ["nul", "très faible", "faible", "moyen", "élevé", "très eleve"]

ICONS = {
    0: "mdi:check",
    1: "mdi:check",
    2: "mdi:alert-outline",
    3: "mdi:alert-outline",
    4: "mdi:alert",
    5: "mdi:alert",
}

ATTRIBUTION = "Data from Reseau National de Surveillance Aerobiologique "

CONF_LOCATIONS = "location"
CONF_TIMEOUT   = "timeout"
CONF_SCANINTERVAL = "scaninterval"

SCAN_INTERVAL = timedelta(minutes=30)
TIMEOUT = 30

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_LOCATIONS): cv.string,
        vol.Optional(CONF_TIMEOUT, default=TIMEOUT): cv.positive_int,
        vol.Optional(CONF_SCANINTERVAL, default=SCAN_INTERVAL): cv.time_period,
    }
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the requested Pollens location."""
    
    county_number = config.get(CONF_LOCATIONS)
    timeout = config.get(CONF_TIMEOUT)
    scan_interval = config.get(CONF_SCAN_INTERVAL)
    
    dev = []
    client = PollensClient(async_get_clientsession(hass), timeout=timeout)
    try:
        resp = json.loads(await client.Get(number=county_number))
        county_name = resp["countyName"]
        pollens_sensor = PollensSensor(client, county_number, county_name)
        dev.append(pollens_sensor)
    except (
        aiohttp.client_exceptions.ClientConnectorError,
        asyncio.TimeoutError,
    ) as err:
        _LOGGER.exception("Failed to connect to  servers")
        raise PlatformNotReady from err
    async_add_entities(dev, True)


class PollensSensor(Entity):
    """Implementation of a WAQI sensor."""

    def __init__(self, client, county_number, county_name):
        """Initialize the sensor."""
        self._client = client

        try:
            self.county_name = county_name
            self.county_number = county_number
            _LOGGER.info("Init pollens sensor for %s county",self.county_name)
        except (KeyError, TypeError):
            self.county_name = None
            self.county_number = None

        self._data = None

    @property
    def name(self):
        """Return the name of the sensor."""
        if self.county_name:
            return f"pollens {self.county_name}"
        return "pollens {}".format(county_number)

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
    def device_state_attributes(self):
        """Return the state attributes of the last update."""
        attrs = {}

        if self._data is not None:
            try:
                _LOGGER.debug("%s: Update attributes", self.name)
                attrs[ATTR_ATTRIBUTION] = ATTRIBUTION
                attrs[ATTR_URL] = "https://pollens.fr"
                attrs[ATTR_COUNTY_NAME] = self.county_name
            
                risks = [item for item in self._data["risks"] if item["level"] > 0]
                _LOGGER.info("%d risque(s) superieur à 0", len(risks))
                for risk in risks:
                    _LOGGER.info("- Risque %s : %d", risk["pollenName"], risk["level"] )
                    attrs[KEY_TO_ATTR[risk["pollenName"].lower()]] = LIST_RISK[risk["level"]]
                return attrs
            except (IndexError, KeyError) as err:
                _LOGGER.warning("%s: Attribution exception %s", self.name, "error {}".format(err))
                return {ATTR_ATTRIBUTION: ATTRIBUTION}

    async def async_update(self):
        """Get the latest data and updates the states and attributes."""
        if self.county_number:
            _LOGGER.debug("%s: Updating sensor pollens for %s", self.name, self.county_name)
            result = json.loads(await self._client.Get(number=self.county_number))
            _LOGGER.debug("%s: Pollens sensor updated. receive %d", self.name, sys.getsizeof(result))
        else:
            result = None
        self._data = result
