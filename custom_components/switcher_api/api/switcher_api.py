"""Request handlers for the Switcher WebAPI."""
from datetime import time
import json
import logging
import sys
from typing import List, Optional

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession

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
        self._session = None
        self._base_url = None

    @property
    def config_data(self):
        return self._config_manager.data

    @property
    def ssl_context(self):
        return False if self.config_data.is_ssl else None

    @staticmethod
    def _is_success(response):
        is_success = response and response.get(KEY_SUCCESSFUL, False)

        return is_success

    async def initialize(self):
        _LOGGER.info("Initializing Switcher API")

        try:
            config_data = self.config_data

            self._base_url = (
                f"{config_data.protocol}://{config_data.host}:{config_data.port}"
            )

            if self._hass is None:
                if self._session is not None:
                    await self._session.close()

                self._session = aiohttp.client.ClientSession()
            else:
                self._session = async_create_clientsession(hass=self._hass)

            _LOGGER.debug(f"Initialized Switch API with URL: {self._base_url}")

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(
                f"Failed to initialize Switcher API ({self._base_url}), error: {ex}, line: {line_number}"
            )

    async def async_update(self):
        state = await self.get_state()

        if state:
            _LOGGER.debug(f"State: {state}")
            self.state = state

        schedules = await self.get_schedules()

        if schedules:
            _LOGGER.debug(f"Schedules: {schedules}")
            self.schedules = schedules

    async def _async_post(self, endpoint, data: Optional[dict] = None):
        result = None

        try:
            _LOGGER.debug(f"Starting to POST {endpoint}, Data: {data}")

            url = f"{self._base_url}{endpoint}"

            async with self._session.post(
                url, data=json.dumps(data), ssl=self.ssl_context
            ) as response:
                _LOGGER.debug(f"Status of {url}: {response.status}")

                response.raise_for_status()

                result = await response.json()

                if not self._is_success(result):
                    _LOGGER.warning(f"{endpoint} return failed result: {result}")

                    result = None

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(
                f"Failed to POST {endpoint}, Error: {ex}, Line: {line_number}"
            )

        return result

    async def _async_get(self, endpoint):
        result = None

        try:
            _LOGGER.debug(f"Starting to GET {endpoint}")

            url = f"{self._base_url}{endpoint}"

            async with self._session.get(url, ssl=self.ssl_context) as response:
                _LOGGER.debug(f"Status of {url}: {response.status}")

                response.raise_for_status()

                result = await response.json()

                if not self._is_success(result):
                    _LOGGER.warning(f"{endpoint} return failed result: {result}")

                    result = None

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f"Failed to GET {endpoint}, Error: {ex}, Line: {line_number}")

        return result

    async def _async_delete(self, endpoint):
        result = None

        try:
            _LOGGER.debug(f"Starting to DELETE {endpoint}")

            url = f"{self._base_url}{endpoint}"

            async with self._session.delete(url, ssl=self.ssl_context) as response:
                _LOGGER.debug(f"Status of {url}: {response.status}")

                response.raise_for_status()

                result = await response.json()

                if not self._is_success(result):
                    _LOGGER.warning(f"{endpoint} return failed result: {result}")

                    result = None

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(
                f"Failed to DELETE {endpoint}, Error: {ex}, Line: {line_number}"
            )

        return result

    async def _async_patch(self, endpoint, data: Optional[dict] = None):
        result = None

        try:
            _LOGGER.debug(f"Starting to PATCH {endpoint}, Data: {data}")

            url = f"{self._base_url}{endpoint}"

            async with self._session.patch(
                url, data=json.dumps(data), ssl=self.ssl_context
            ) as response:
                _LOGGER.debug(f"Status of {url}: {response.status}")

                response.raise_for_status()

                result = await response.json()

                if not self._is_success(result):
                    _LOGGER.warning(f"{endpoint} return failed result: {result}")

                    result = None

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(
                f"Failed to PATCH {endpoint}, Error: {ex}, Line: {line_number}"
            )

        return result

    async def _async_put(self, endpoint, data: Optional[dict] = None):
        result = None

        try:
            _LOGGER.debug(f"Starting to PUT {endpoint}, Data: {data}")

            url = f"{self._base_url}{endpoint}"

            async with self._session.put(
                url, data=json.dumps(data), ssl=self.ssl_context
            ) as response:
                _LOGGER.debug(f"Status of {url}: {response.status}")

                response.raise_for_status()

                result = await response.json()

                if not self._is_success(result):
                    _LOGGER.warning(f"{endpoint} return failed result: {result}")

                    result = None

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f"Failed to PUT {endpoint}, Error: {ex}, Line: {line_number}")

        return result

    async def create_schedule(self, days: List[str], start_time: time, stop_time: time):
        is_success = False

        try:
            data = {
                PARAM_DAYS: days,
                PARAM_START_HOURS: start_time.hour,
                PARAM_START_MINUTES: start_time.minute,
                PARAM_STOP_HOURS: stop_time.hour,
                PARAM_STOP_MINUTES: stop_time.minute,
            }

            response = await self._async_put(ENDPOINT_CREATE_SCHEDULE, data)

            is_success = response is not None

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(f"Failed creating new schedule, Error: {ex}, Line: {line}")

        return is_success

    async def delete_schedule(self, schedule_id: str):
        """Use for handling requests to /switcher_api/delete_schedule."""
        is_success = False

        try:
            endpoint = f"{ENDPOINT_DISABLE_SCHEDULE}?{PARAM_SCHEDULE_ID}={schedule_id}"

            response = await self._async_delete(endpoint)

            is_success = response is not None

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(f"Failed deleting schedule, Error: {ex}, Line: {line}")

        return is_success

    async def disable_schedule(self, schedule_data: str):
        """Use for handling requests to /switcher_api/disable_schedule."""
        is_success = False

        try:
            data = {
                PARAM_SCHEDULE_DATA: schedule_data,
            }

            response = await self._async_patch(ENDPOINT_DISABLE_SCHEDULE, data)

            is_success = response is not None

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(f"Failed disabling schedule, Error: {ex}, Line: {line}")

        return is_success

    async def enable_schedule(self, schedule_data: str):
        """Use for handling requests to /switcher_api/enable_schedule."""
        is_success = False

        try:
            data = {
                PARAM_SCHEDULE_DATA: schedule_data,
            }

            response = await self._async_patch(ENDPOINT_ENABLE_SCHEDULE, data)

            is_success = response is not None

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(f"Failed enabling schedule, Error: {ex}, Line: {line}")

        return is_success

    async def get_schedules(self):
        """Use for handling requests to /switcher_api/get_schedules."""
        response = None

        try:
            response = await self._async_get(ENDPOINT_GET_SCHEDULES)
        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(
                f"Failed to get the device schedules, Error: {ex}, Line: {line}"
            )

        return response

    async def get_state(self):
        """Use for handling requests to /switcher_api/get_state."""
        response = None

        try:
            response = await self._async_get(ENDPOINT_GET_STATE)
        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(f"Failed to get the device state, Error: {ex}, Line: {line}")

        return response

    async def set_auto_shutdown(self, time_span: time):
        """Use for handling requests to /switcher_api/set_auto_shutdown."""
        is_success = False

        try:
            data = {PARAM_HOURS: time_span.hour, PARAM_MINUTES: time_span.minute}

            response = await self._async_post(ENDPOINT_SET_AUTO_SHUTDOWN, data)

            is_success = response is not None

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(
                f"Failed setting auto shutdown on device, Error: {ex}, Line: {line}"
            )

        return is_success

    async def set_device_name(self, new_name):
        """Use for handling requests to /switcher_api/set_device_name."""
        is_success = False

        try:
            data = {PARAM_NAME: new_name}

            response = await self._async_post(ENDPOINT_SET_DEVICE_NAME, data)

            is_success = response is not None

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(f"Failed setting the device name, Error: {ex}, Line: {line}")

        return is_success

    async def turn_off(self):
        """Use for handling requests to /switcher_api/turn_off."""
        is_success = False
        try:
            response = await self._async_post(ENDPOINT_TURN_OFF)

            is_success = response is not None

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(f"Failed turning off the device, Error: {ex}, Line: {line}")

        return is_success

    async def turn_on(self, minutes: Optional[str] = None):
        """Use for handling requests to /switcher_api/turn_on."""
        is_success = False
        try:
            data = None
            if minutes is not None:
                data = {PARAM_MINUTES: minutes}

            response = await self._async_post(ENDPOINT_TURN_ON, data)

            is_success = response is not None
        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line = tb.tb_lineno

            _LOGGER.error(f"Failed turning on the device, Error: {ex}, Line: {line}")

        return is_success
