"""Request handlers for the Switcher WebAPI."""
from datetime import time
import logging
import sys
from typing import List, Optional

from aioswitcher.api import Command, SwitcherApi as SwitcherClient
from aioswitcher.schedule import Days

from homeassistant.core import HomeAssistant

from . import _serialize_object
from ..helpers.const import *
from ..managers.configuration_manager import ConfigManager

_LOGGER = logging.getLogger(__name__)


class SwitcherApi:
    state: dict
    schedules: dict

    def __init__(self, hass: HomeAssistant, config_manager: ConfigManager):
        self._hass = hass
        self._config_manager = config_manager
        self.schedules = {}
        self.state = {}

    @property
    def config_data(self):
        return self._config_manager.data

    @property
    def ip_address(self):
        return self.config_data.ip_address

    @property
    def device_id(self):
        return self.config_data.device_id

    @property
    def device_details(self):
        return f"IP: {self.ip_address}, Device: {self.device_id}"

    async def async_update_state(self):
        state = await self.get_state()

        if state:
            _LOGGER.debug(f"State: {state}")
            self.state = state

    async def async_update_schedule(self):
        schedules = await self.get_schedules()

        if schedules:
            _LOGGER.debug(f"Schedules: {schedules}")
            self.schedules = schedules

    async def create_schedule(self, days: List[str], start_time: str, stop_time: str):
        is_success = False

        try:
            weekdays = dict(map(lambda d: (d.value, d), Days))
            selected_days = (
                {weekdays[d] for d in days[KEY_DAYS]} if days else set()
            )

            async with SwitcherClient(self.ip_address, self.device_id) as api:
                state = await api.create_schedule(start_time, stop_time, selected_days)
                _LOGGER.debug(f"Create Schedule request returned: {state}")

                response = _serialize_object(state)

                is_success = response is not None

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(f"Failed creating new schedule, {self.device_details}, Error: {ex}, Line: {line}")

        return is_success

    async def delete_schedule(self, schedule_id: str):
        """Use for handling requests to /switcher_api/delete_schedule."""
        is_success = False

        try:
            async with SwitcherClient(self.ip_address, self.device_id) as api:
                state = await api.delete_schedule(schedule_id)
                _LOGGER.debug(f"Delete Schedule request returned: {state}")

                response = _serialize_object(state)

                is_success = response is not None

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(f"Failed deleting schedule, {self.device_details}, Error: {ex}, Line: {line}")

        return is_success

    async def get_schedules(self):
        """Use for handling requests to /switcher_api/get_schedules."""
        response = None

        try:
            async with SwitcherClient(self.ip_address, self.device_id) as api:
                state = await api.get_schedules()
                _LOGGER.debug(f"Get Schedules request returned: {state}")

                response = _serialize_object(state)

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(
                f"Failed to get the device schedules, {self.device_details}, Error: {ex}, Line: {line}"
            )

        return response

    async def get_state(self) -> dict:
        """Use for handling requests to /switcher_api/get_state."""
        response = None

        try:
            async with SwitcherClient(self.ip_address, self.device_id) as api:
                state = await api.get_state()
                _LOGGER.debug(f"Get State request returned: {state}")

                response = _serialize_object(state)

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(f"Failed to get the device state, {self.device_details}, Error: {ex}, Line: {line}")

        return response

    async def set_auto_shutdown(self, time_span: time):
        """Use for handling requests to /switcher_api/set_auto_shutdown."""
        is_success = False

        try:
            async with SwitcherClient(self.ip_address, self.device_id) as api:
                auto_shutdown = timedelta(hours=time_span.hour, minutes=time_span.minute)
                state = await api.set_auto_shutdown(auto_shutdown)
                _LOGGER.debug(f"Set Automatic Shutdown request returned: {state}")

                response = _serialize_object(state)

                is_success = response is not None

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(
                f"Failed setting auto shutdown on device, {self.device_details}, Error: {ex}, Line: {line}"
            )

        return is_success

    async def set_device_name(self, new_name: str):
        """Use for handling requests to /switcher_api/set_device_name."""
        is_success = False

        try:
            async with SwitcherClient(self.ip_address, self.device_id) as api:
                state = await api.set_device_name(new_name)
                _LOGGER.debug(f"Set Device Name request returned: {state}")

                response = _serialize_object(state)

                is_success = response is not None

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(f"Failed setting the device name, {self.device_details}, Error: {ex}, Line: {line}")

        return is_success

    async def turn_off(self):
        """Use for handling requests to /switcher_api/turn_off."""
        is_success = False
        try:
            async with SwitcherClient(self.ip_address, self.device_id) as api:
                state = await api.control_device(Command.OFF)
                _LOGGER.debug(f"Turn Off request returned: {state}")

                response = _serialize_object(state)

                is_success = response is not None

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(f"Failed turning off the device, {self.device_details}, Error: {ex}, Line: {line}")

        return is_success

    async def turn_on(self, minutes: Optional[int] = 0):
        """Use for handling requests to /switcher_api/turn_on."""
        is_success = False
        try:
            async with SwitcherClient(self.ip_address, self.device_id) as api:
                state = await api.control_device(Command.ON, minutes)
                _LOGGER.debug(f"Turn On request returned: {state}")

                response = _serialize_object(state)

                is_success = response is not None
        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(f"Failed turning on the device, {self.device_details}, Error: {ex}, Line: {line}")

        return is_success
