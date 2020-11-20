import logging
from typing import Any, Dict, Optional

from cryptography.fernet import InvalidToken
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST

from .. import get_ha
from ..api.switcher_api import SwitcherApi
from ..helpers.const import *
from ..managers.configuration_manager import ConfigManager
from ..models import LoginError
from ..models.config_data import ConfigData

_LOGGER = logging.getLogger(__name__)


class ConfigFlowManager:
    _config_manager: ConfigManager
    _options: Optional[dict]
    _data: Optional[dict]
    _config_entry: Optional[ConfigEntry]
    api: Optional[SwitcherApi]
    title: str

    def __init__(self):
        self._config_entry = None

        self._options = None
        self._data = None

        self._is_initialized = True
        self._hass = None
        self.api = None
        self.title = DEFAULT_NAME

    async def initialize(self, hass, config_entry: Optional[ConfigEntry] = None):
        self._config_entry = config_entry
        self._hass = hass

        self._config_manager = ConfigManager()

        data = {}
        options = {}

        if self._config_entry is not None:
            data = self._config_entry.data
            options = self._config_entry.options

            self.title = self._config_entry.title

        await self.update_data(data, CONFIG_FLOW_INIT)
        await self.update_options(options, CONFIG_FLOW_INIT)

    @property
    def config_data(self) -> ConfigData:
        return self._config_manager.data

    async def update_options(self, options: dict, flow: str):
        _LOGGER.debug("Update options")
        validate_login = False

        new_options = await self._clone_items(options, flow)

        self._options = new_options

        await self._update_entry()

        if validate_login:
            await self._handle_data(flow)

        return new_options

    async def update_data(self, data: dict, flow: str):
        _LOGGER.debug("Update data")

        self._data = await self._clone_items(data, flow)

        await self._update_entry()

        await self._handle_data(flow)

        return self._data

    def _get_default_fields(
        self, flow, config_data: Optional[ConfigData] = None
    ) -> Dict[vol.Marker, Any]:
        if config_data is None:
            config_data = self.config_data

        fields = {
            vol.Optional(CONF_HOST, default=config_data.host): str,
            vol.Optional(CONF_DEVICE_ID, default=config_data.device_id): str,
        }

        return fields

    async def get_default_data(self, user_input) -> vol.Schema:
        config_data = await self._config_manager.get_basic_data(user_input)

        fields = self._get_default_fields(CONFIG_FLOW_DATA, config_data)

        data_schema = vol.Schema(fields)

        return data_schema

    def get_default_options(self) -> vol.Schema:
        config_data = self.config_data

        fields = self._get_default_fields(CONFIG_FLOW_OPTIONS)

        fields[vol.Optional(CONF_LOG_LEVEL, default=config_data.log_level)] = vol.In(
            LOG_LEVELS
        )

        data_schema = vol.Schema(fields)

        return data_schema

    async def _update_entry(self):
        try:
            entry = ConfigEntry(
                0, "", "", self._data, "", "", {}, options=self._options
            )

            await self._config_manager.update(entry)
        except InvalidToken:
            entry = ConfigEntry(
                0, "", "", self._data, "", "", {}, options=self._options
            )

            await self._config_manager.update(entry)

    @staticmethod
    async def _clone_items(user_input, flow: str):
        new_user_input = {}

        if user_input is not None:
            for key in user_input:
                user_input_data = user_input[key]

                new_user_input[key] = user_input_data

        return new_user_input

    @staticmethod
    def clone_items(user_input):
        new_user_input = {}

        if user_input is not None:
            for key in user_input:
                user_input_data = user_input[key]

                new_user_input[key] = user_input_data

        return new_user_input

    def _get_ha(self, key: str = None):
        if key is None:
            key = self.title

        ha = get_ha(self._hass, key)

        return ha

    async def _handle_data(self, flow):
        if flow != CONFIG_FLOW_INIT:
            await self._valid_login()

        if flow == CONFIG_FLOW_OPTIONS:
            config_entries = self._hass.config_entries
            config_entries.async_update_entry(self._config_entry, data=self._data)

    async def _valid_login(self):
        errors = None

        config_data = self._config_manager.data

        api = SwitcherApi(self._hass, self._config_manager)
        state = await api.get_state()

        if state is None:
            _LOGGER.warning(f"Failed to access Switcher ({config_data.host})")
            errors = {"base": "invalid_server_details"}
        else:
            system_name = f"{DEFAULT_NAME} ({config_data.host})"

            if system_name is not None:
                self.title = system_name

        if errors is not None:
            raise LoginError(errors)
