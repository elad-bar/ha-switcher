"""
Support for Sensors.
"""
import logging
from typing import Union

from homeassistant.core import HomeAssistant

from .helpers.const import *
from .models.base_entity import BaseEntity, async_setup_base_entry
from .models.entity_data import EntityData

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = [DOMAIN]

CURRENT_DOMAIN = DOMAIN_SENSOR


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Set up the Switcher Binary Sensor."""
    await async_setup_base_entry(
        hass, config_entry, async_add_devices, CURRENT_DOMAIN, get_sensor
    )


async def async_unload_entry(hass, config_entry):
    _LOGGER.info(f"async_unload_entry {CURRENT_DOMAIN}: {config_entry}")

    return True


def get_sensor(hass: HomeAssistant, host: str, entity: EntityData):
    sensor = Sensor()
    sensor.initialize(hass, host, entity, CURRENT_DOMAIN)

    return sensor


class Sensor(BaseEntity):
    """Representation a binary sensor that is updated by Switcher."""

    @property
    def state(self) -> Union[None, str, int, float]:
        """Return the state of the sensor."""
        return self.entity.state

    async def async_added_to_hass_local(self):
        _LOGGER.info(f"Added new {self.name}")

    def _immediate_update(self, previous_state: bool):
        if previous_state != self.entity.state:
            _LOGGER.debug(
                f"{self.name} updated from {previous_state} to {self.entity.state}"
            )

        super()._immediate_update(previous_state)
