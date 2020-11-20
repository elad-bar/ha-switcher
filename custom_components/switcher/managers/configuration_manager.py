import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST

from ..helpers.const import *
from ..models.config_data import ConfigData

_LOGGER = logging.getLogger(__name__)


class ConfigManager:
    data: ConfigData
    config_entry: ConfigEntry

    async def update(self, config_entry: ConfigEntry):
        data = config_entry.data
        options = config_entry.options

        result: ConfigData = await self.get_basic_data(data)

        result.log_level = options.get(CONF_LOG_LEVEL, LOG_LEVEL_DEFAULT)
        result.device_id = data.get(CONF_DEVICE_ID)
        result.host = data.get(CONF_HOST)

        self.config_entry = config_entry
        self.data = result

    @staticmethod
    async def get_basic_data(data):
        result = ConfigData()

        if data is not None:
            result.host = data.get(CONF_HOST)
            result.device_id = data.get(CONF_DEVICE_ID)

        return result
