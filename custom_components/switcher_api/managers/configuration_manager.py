import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_IP_ADDRESS

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
        result.ip_address = data.get(CONF_IP_ADDRESS)
        result.auto_off = options.get(CONF_AUTO_OFF)

        self.config_entry = config_entry
        self.data = result

    @staticmethod
    async def get_basic_data(data):
        result = ConfigData()

        if data is not None:
            result.ip_address = data.get(CONF_IP_ADDRESS)
            result.device_id = data.get(CONF_DEVICE_ID)

        return result
