"""Request handlers for the Switcher WebAPI."""
from datetime import datetime, time
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
    last_update: datetime
    is_updating: bool

    def __init__(self, hass: HomeAssistant, config_manager: ConfigManager):
        self._hass = hass
        self._config_manager = config_manager
        self.schedules = {}
        self.state = {}
        self.last_update = datetime.utcnow()
        self.is_updating = False

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

    async def async_update(self):
        if not self.is_updating:
            self.is_updating = True

            now = datetime.utcnow()
            time_since_last_updated = now - self.last_update
            seconds_since_last_updated = time_since_last_updated.total_seconds()
            should_update_schedules = seconds_since_last_updated >= 60

            state = await self._get_state()

            if state:
                _LOGGER.debug(f"State: {state}")
                self.state = state

            if should_update_schedules:
                schedules = await self._get_schedules()

                if schedules:
                    _LOGGER.debug(f"Schedules: {schedules}")
                    self.schedules = schedules

            self.last_update = datetime.utcnow()
            self.is_updating = False

    async def create_schedule(self, days: List[str], start_time: str, stop_time: str):
        is_success = False

        try:
            weekdays = dict(map(lambda d: (d.value, d), Days))
            selected_days = (
                {weekdays[d] for d in days[KEY_DAYS]} if days else set()
            )

            async with SwitcherClient(self.ip_address, self.device_id) as api:
                state = await api.create_schedule(start_time, stop_time, selected_days)

                if state.successful:
                    _LOGGER.debug(f"Create Schedule successfully completed, Response: {state}")
                else:
                    _LOGGER.error(f"Failed to Create Schedule")

                is_success = state.successful

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(f"Failed creating new schedule, {self.device_details}, Error: {ex}, Line: {line}")

        return is_success

    async def delete_schedule(self, schedule_id: str):
        is_success = False

        try:
            async with SwitcherClient(self.ip_address, self.device_id) as api:
                state = await api.delete_schedule(schedule_id)

                if state.successful:
                    _LOGGER.debug(f"Delete Schedule successfully completed, Response: {state}")
                else:
                    _LOGGER.error(f"Failed to Delete Schedule")

                is_success = state.successful

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(f"Failed deleting schedule, {self.device_details}, Error: {ex}, Line: {line}")

        return is_success

    async def _get_schedules(self):
        response = None

        try:
            async with SwitcherClient(self.ip_address, self.device_id) as api:
                state = await api.get_schedules()

                if state.successful:
                    response = _serialize_object(state)
                    _LOGGER.debug(f"Retrieve schedules successfully completed, Response: {state}")

                else:
                    _LOGGER.error(f"Failed to retrieve schedules")

        except GeneratorExit as gex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno
            error_details = f"Generator Exit Error: {gex.args}, Line: {line}"

            _LOGGER.error(f"Failed to get the device, {self.device_details}, {error_details}")

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(
                f"Failed to get the device ,schedules {self.device_details}, Error: {ex}, Line: {line}"
            )

        return response

    async def _get_state(self) -> dict:
        response = None

        try:
            async with SwitcherClient(self.ip_address, self.device_id) as api:
                state = await api.get_state()

                if state.successful:
                    response = _serialize_object(state)
                    _LOGGER.debug(f"Retrieved state successfully completed, Response: {state}")

                else:
                    _LOGGER.error(f"Failed to retrieve state")

        except GeneratorExit as gex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            error_details = f"Generator Exit Error: {gex.args}, Line: {line}"

            _LOGGER.error(f"Failed to get the device state, {self.device_details}, {error_details}")

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(f"Failed to get the device state, {self.device_details}, Error: {ex}, Line: {line}")

        return response

    async def set_auto_shutdown(self, time_span: time):
        is_success = False

        try:
            async with SwitcherClient(self.ip_address, self.device_id) as api:
                auto_shutdown = timedelta(hours=time_span.hour, minutes=time_span.minute)
                state = await api.set_auto_shutdown(auto_shutdown)

                if state.successful:
                    _LOGGER.debug(f"Auto Shutdown Set successfully completed, Response: {state}")
                else:
                    _LOGGER.error(f"Failed to Set Auto Shutdown")

                is_success = state.successful

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(
                f"Failed setting auto shutdown on device, {self.device_details}, Error: {ex}, Line: {line}"
            )

        return is_success

    async def set_device_name(self, new_name: str):
        is_success = False

        try:
            async with SwitcherClient(self.ip_address, self.device_id) as api:
                state = await api.set_device_name(new_name)

                if state.successful:
                    _LOGGER.debug(f"Device Name Set successfully completed, Response: {state}")
                else:
                    _LOGGER.error(f"Failed to Set Device Name")

                is_success = state.successful

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(f"Failed setting the device name, {self.device_details}, Error: {ex}, Line: {line}")

        return is_success

    async def turn_off(self):
        is_success = await self._toggle_state(False)

        return is_success

    async def turn_on(self, minutes: Optional[int] = 0):
        is_success = await self._toggle_state(True, minutes)

        return is_success

    async def _toggle_state(self, action: bool, minutes: Optional[int] = 0):
        is_success = False
        command = Command.ON if action else Command.OFF
        command_name = "On" if action else "Off"

        try:
            async with SwitcherClient(self.ip_address, self.device_id) as api:
                state = await api.control_device(command, minutes)

                if state.successful:
                    _LOGGER.debug(f"Turn {command_name} successfully completed, Response: {state}")

                    await self.async_update()

                else:
                    _LOGGER.error(f"Failed to Turn {command_name}, {self.device_details}")

                is_success = state.successful

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(f"Failed to Turn {command_name} the device, {self.device_details}, Error: {ex}, Line: {line}")

        return is_success
