"""
Support for Switcher.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.switcher/
"""
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant

from .helpers.const import *
from .models.base_entity import BaseEntity, async_setup_base_entry
from .models.entity_data import EntityData

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = [DOMAIN]

CURRENT_DOMAIN = DOMAIN_SWITCH


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Set up the Switcher Switch."""
    await async_setup_base_entry(
        hass, config_entry, async_add_devices, CURRENT_DOMAIN, get_switch
    )


async def async_unload_entry(hass, config_entry):
    _LOGGER.info(f"async_unload_entry {CURRENT_DOMAIN}: {config_entry}")

    return True


def get_switch(hass: HomeAssistant, host: str, entity: EntityData):
    switch = Switch()
    switch.initialize(hass, host, entity, CURRENT_DOMAIN)

    return switch


class Switch(SwitchEntity, BaseEntity):
    """Class for an Switcher switch."""

    @property
    def is_on(self):
        """Return the boolean response if the node is on."""
        return self.entity.state

    @property
    def icon(self):
        """Return the boolean response if the node is on."""
        return self.entity.icon

    async def async_turn_on(self, **kwargs):
        """Turn device on."""
        if self.entity_type == SWITCH_MAIN:
            await self.api.turn_on()

            await self.api.async_update_state()
        else:
            details = self.entity.details
            schedule_data = details.get(KEY_SCHEDULE_DATA)

            await self.api.enable_schedule(schedule_data)

            await self.api.async_update_schedule()

        self.ha.async_update()

    async def async_turn_off(self, **kwargs):
        """Turn device off."""
        if self.entity_type == SWITCH_MAIN:
            await self.api.turn_off()

            await self.api.async_update_state()
        else:
            details = self.entity.details
            schedule_data = details.get(KEY_SCHEDULE_DATA)

            await self.api.disable_schedule(schedule_data)

            await self.api.async_update_schedule()

        self.ha.async_update()

    def turn_on(self, **kwargs) -> None:
        pass

    def turn_off(self, **kwargs) -> None:
        pass

    async def async_setup(self):
        pass

    def _immediate_update(self, previous_state: bool):
        if previous_state != self.entity.state:
            _LOGGER.debug(
                f"{self.name} updated from {previous_state} to {self.entity.state}"
            )

        super()._immediate_update(previous_state)
