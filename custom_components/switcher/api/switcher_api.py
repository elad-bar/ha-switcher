"""Request handlers for the Switcher WebAPI."""
from datetime import time
import logging
from typing import Dict, List, Optional

from aioswitcher.api import SwitcherV2Api, messages
from aioswitcher.consts import (
    COMMAND_OFF,
    COMMAND_ON,
    DAY_TO_INT_DICT,
    DISABLE_SCHEDULE,
    ENABLE_SCHEDULE,
    SCHEDULE_CREATE_DATA_FORMAT,
)
from aioswitcher.schedules import calc_next_run_for_schedule
from aioswitcher.tools import create_weekdays_value, timedelta_str_to_schedule_time

from homeassistant.core import HomeAssistant

from ..helpers.const import *
from ..managers.configuration_manager import ConfigManager

_LOGGER = logging.getLogger(__name__)


class SwitcherApi:
    state: dict
    schedules: List

    def __init__(self, hass: HomeAssistant, config_manager: ConfigManager):
        self._hass = hass
        self._config_manager = config_manager
        self._api = None
        self.schedules = []
        self.state = {}

    @property
    def config_data(self):
        return self._config_manager.data

    async def async_update(self):
        self.schedules = await self.get_schedules()
        self.state = await self.get_state()

    def get_running_loop(self):
        return self._hass.loop

    async def initialize(self):
        self._api = await SwitcherV2Api(
            self.get_running_loop(),
            self.config_data.host,
            self.config_data.phone_id,
            self.config_data.device_id,
            self.config_data.device_password,
        )

    @staticmethod
    def _is_success(response, expected_result):
        is_success = response and response.msg_type == expected_result

        return is_success

    async def create_schedule(
        self, days: List[str], recurring: bool, start_time: time, stop_time: time
    ):
        is_success = False

        """Use for handling requests to /switcher/create_schedule."""
        try:
            schedule_days = [0]
            if recurring:
                for day in days:
                    schedule_days.append(DAY_TO_INT_DICT(day))

            running_loop = self.get_running_loop()

            weekdays = await create_weekdays_value(running_loop, schedule_days)
            start_time = await timedelta_str_to_schedule_time(
                running_loop,
                str(timedelta(hours=start_time.hour, minutes=start_time.minute)),
            )

            end_time = await timedelta_str_to_schedule_time(
                running_loop,
                str(timedelta(hours=stop_time.hour, minutes=stop_time.minute)),
            )

            schedule_data = SCHEDULE_CREATE_DATA_FORMAT.format(
                weekdays, start_time, end_time
            )

            response = await self._api.create_schedule(schedule_data)

            is_success = self._is_success(
                response, messages.ResponseMessageType.CREATE_SCHEDULE
            )

        except Exception as ex:
            _LOGGER.error(f"Failed creating the schedule, Error: {ex}")

        return is_success

    async def delete_schedule(self, schedule_id: str):
        """Use for handling requests to /switcher/delete_schedule."""
        is_success = False

        try:
            response = await self._api.delete_schedule(schedule_id)

            is_success = self._is_success(
                response, messages.ResponseMessageType.DELETE_SCHEDULE
            )
        except Exception as ex:
            _LOGGER.error(f"Failed deleting the schedule, Error: {ex}")

        return is_success

    async def disable_schedule(self, schedule_data: str):
        """Use for handling requests to /switcher/disable_schedule."""
        is_success = False

        try:
            if len(schedule_data) == 24:
                updated_schedule_data = (
                    schedule_data[0:2] + DISABLE_SCHEDULE + schedule_data[4:]
                )

                response = await self._api.disable_enable_schedule(
                    updated_schedule_data
                )

                is_success = self._is_success(
                    response, messages.ResponseMessageType.DISABLE_ENABLE_SCHEDULE
                )
            else:
                _LOGGER.error("Argument schedule_data is length is no 24.")

        except Exception as ex:
            _LOGGER.error(f"Failed disabling the schedule, Error: {ex}")

        return is_success

    async def enable_schedule(self, schedule_data: str):
        """Use for handling requests to /switcher/enable_schedule."""
        is_success = False

        try:
            if len(schedule_data) == 24:
                updated_schedule_data = (
                    schedule_data[0:2] + ENABLE_SCHEDULE + schedule_data[4:]
                )

                response = await self._api.disable_enable_schedule(
                    updated_schedule_data
                )

                is_success = self._is_success(
                    response, messages.ResponseMessageType.DISABLE_ENABLE_SCHEDULE
                )
            else:
                _LOGGER.error("Argument schedule_data is length is no 24.")

        except Exception as ex:
            _LOGGER.error(f"Failed disabling the schedule, Error: {ex}")

        return is_success

    async def get_schedules(self):
        """Use for handling requests to /switcher/get_schedules."""
        schedules_list = []

        try:
            response = await self._api.get_schedules()
            loop = self._hass.loop

            if response and response.successful:
                schedules_list = []  # type: List[Dict]
                if response.found_schedules:
                    for schedule in response.get_schedules:
                        await schedule.init_future
                        schedule_obj = schedule.init_future.result()
                        next_run = await calc_next_run_for_schedule(loop, schedule_obj)

                        schedules_list.append(
                            {
                                KEY_SCHEDULE_ID: schedule_obj.schedule_id,
                                KEY_ENABLED: schedule_obj.enabled,
                                KEY_RECURRING: schedule_obj.recurring,
                                KEY_DAYS: schedule_obj.days,
                                KEY_START_TIME: schedule_obj.start_time,
                                KEY_END_TIME: schedule_obj.end_time,
                                KEY_DURATION: schedule_obj.duration,
                                KEY_SCHEDULE_DATA: schedule_obj.schedule_data,  # noqa: E501
                                KEY_NEXT_RUN: next_run,
                            }
                        )

        except Exception as ex:
            _LOGGER.error(f"Failed to get the device schedules, Error: {ex}")

        return schedules_list

    async def get_state(self):
        """Use for handling requests to /switcher/get_state."""
        data = None
        try:
            response = await self._api.get_state()

            if response:
                await response.init_future
                state = response.init_future.result()

                is_success = (
                    self._is_success(state, messages.ResponseMessageType.STATE)
                    and state.successful
                )

                if is_success:
                    data = {
                        KEY_SUCCESSFUL: state.successful,
                        KEY_STATE: state.state,
                        KEY_TIME_LEFT: state.time_left,
                        KEY_TIME_ON: state.time_on,
                        KEY_AUTO_OFF: state.auto_off,
                        KEY_POWER_CONSUMPTION: state.power,
                        KEY_ELECTRIC_CURRENT: state.current,
                    }

            else:
                _LOGGER.error("Failed to get response from api.")

        except Exception as ex:
            _LOGGER.error(f"Failed to get the device state, Error: {ex}")

        return data

    async def set_auto_shutdown(self, time_span: time):
        """Use for handling requests to /switcher/set_auto_shutdown."""
        is_success = False

        try:
            hours = time_span.hour
            minutes = time_span.minute

            time_guard = (hours * 60 if hours > 0 else 0) + (
                minutes if minutes > 0 else 0
            )

            if time_guard < 59 or time_guard > 180:
                raise Exception("Auto shutdown can be set between 1 and 3 hours.")

            time_to_off_timedelta = timedelta(hours=hours, minutes=minutes)

            response = await self._api.set_auto_shutdown(time_to_off_timedelta)

            is_success = self._is_success(
                response, messages.ResponseMessageType.AUTO_OFF
            )

        except Exception as ex:
            _LOGGER.error(f"Failed setting auto shutdown on device, Error: {ex}")

        return is_success

    async def set_device_name(self, new_name):
        """Use for handling requests to /switcher/set_device_name."""
        is_success = False

        try:
            if len(new_name) < 2 or len(new_name) > 32:
                raise Exception("Only accepts name with length between 2 and 32.")

            response = await self._api.set_device_name(new_name)
            is_success = self._is_success(
                response, messages.ResponseMessageType.UPDATE_NAME
            )

        except Exception as ex:
            _LOGGER.error(f"Failed setting the device name, Error: {ex}")

        return is_success

    async def turn_off(self):
        """Use for handling requests to /switcher/turn_off."""
        is_success = False
        try:
            response = await self._api.control_device(COMMAND_OFF)
            is_success = self._is_success(
                response, messages.ResponseMessageType.CONTROL
            )

        except Exception as ex:
            _LOGGER.error(f"Failed turning off the device, Error: {ex}")

        return is_success

    async def turn_on(self, minutes: Optional[int] = None):
        """Use for handling requests to /switcher/turn_on."""
        is_success = False
        try:
            if minutes:
                response = await self._api.control_device(COMMAND_ON, minutes)
            else:
                response = await self._api.control_device(COMMAND_ON)

            is_success = self._is_success(
                response, messages.ResponseMessageType.CONTROL
            )
        except Exception as ex:
            _LOGGER.error(f"Failed turning on the device, Error: {ex}")

        return is_success
