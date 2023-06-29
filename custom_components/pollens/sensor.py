"""Support for the RNSA pollens service."""

import logging
from warnings import catch_warnings

from yaml import KeyToken
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    LIST_RISK,
    ATTR_URL,
    ATTR_COUNTY_NAME,
    ATTR_POLLEN_NAME,
    ATTR_LITERAL_STATE,
    KEY_TO_ATTR,
    COORDINATOR,
    CONF_POLLENSLIST,
    CONF_LITERAL,
)
from . import PollensEntity, PollensUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

ICONS = {
    0: "mdi:decagram-outline",
    1: "mdi:decagram-check",
    2: "mdi:alert-decagram-outline",
    3: "mdi:alert-decagram",
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup Sensor Plateform"""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    sensors = []
    try:
        enabled_pollens = entry.data[CONF_POLLENSLIST]
    except KeyError:
        enabled_pollens = [pollen for pollen in KEY_TO_ATTR]
    for risk in coordinator.api.risks:
        name = risk
        icon = KEY_TO_ATTR[risk.lower()][1]
        sensors.append(PollenSensor(coordinator, name=name, icon=icon, entry=entry, enabled=name.lower() in enabled_pollens))

    name = f"pollens_{coordinator.county}"
    icon = ICONS[0]
    sensors.append(
        RiskSensor(coordinator=coordinator, name=name, icon=icon, entry=entry, numeric=False)
    )
    sensors.append(
        RiskSensor(coordinator=coordinator, name=name + "_risklevel", icon=icon, entry=entry, numeric=True)
    )

    async_add_entities(sensors, True)


class PollenSensor(PollensEntity, SensorEntity):
    """Implementation of a Pollens sensor."""

    def __init__(
        self,
        coordinator: PollensUpdateCoordinator,
        name: str,
        icon: str,
        entry: ConfigEntry,
        enabled: bool
    ) -> None:
        super().__init__(coordinator, name, icon, entry)
        self._name = f"pollens_{coordinator.county}_{KEY_TO_ATTR[name.lower()][0]}"
        self._state = coordinator.api.risks[name]
        self._unique_id = f"{entry.entry_id}_{self._name}"
        self._attr_name = name
        self._attr_unique_id = self._unique_id
        self._attr_entity_registry_enabled_default = enabled

        try:
            self._literal_state = entry.data[CONF_LITERAL]
            # Setup DeviceClass in AQI and stateClass in numeric (Issue #15)
            if not self._literal_state:
                self._attr_device_class = SensorDeviceClass.AQI
                self._attr_state_class = SensorStateClass.MEASUREMENT

        except KeyError:
            self._literal_state = True
        self._attr_icon = icon
        self._friendly_name = f"{name}"

    @property
    def name(self):
        return self._name

    @property
    def native_value(self):
        value = self.coordinator.api.risks[self._attr_name]
        if self._literal_state:
            return LIST_RISK[value]
        else:
            return value

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the last update."""
        attrs = {}
        attrs[ATTR_POLLEN_NAME] = self._friendly_name
        if self.coordinator.api.risks is not None:
            if not self._literal_state:
                value = self.coordinator.api.risks[self._attr_name]
                attrs[ATTR_LITERAL_STATE] = LIST_RISK[value]
        return attrs


class RiskSensor(PollensEntity, SensorEntity):
    """Implementation of Risk Sensor"""

    def __init__(
        self,
        coordinator: PollensUpdateCoordinator,
        name: str,
        icon: str,
        entry: ConfigEntry,
        numeric: bool
    ) -> None:
        super().__init__(coordinator, name, icon, entry)
        self._risk_level = coordinator.api.risk_level
        self._attr_unique_id = f"{entry.entry_id}_{coordinator.county}"
        self._attr_icon = icon
        self._name = name
        self._numeric = numeric
        if numeric:
            self._attr_unique_id += "_risklevel"
            self._attr_device_class = SensorDeviceClass.AQI
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        value = self.coordinator.api.risk_level
        if self._numeric:
            return value
        else:
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
