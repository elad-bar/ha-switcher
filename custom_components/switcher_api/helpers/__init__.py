import logging
import sys

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from ..managers.home_assistant import HomeAssistantManager
from .const import *

_LOGGER = logging.getLogger(__name__)


def clear_ha(hass: HomeAssistant, entry_id):
    if DATA not in hass.data:
        hass.data[DATA] = dict()

    del hass.data[DATA][entry_id]


def get_ha(hass: HomeAssistant, entry_id):
    ha_data = hass.data.get(DATA, dict())
    ha = ha_data.get(entry_id)

    return ha


async def async_set_ha(hass: HomeAssistant, entry: ConfigEntry):
    try:
        if DATA not in hass.data:
            hass.data[DATA] = dict()

        instance = HomeAssistantManager(hass)

        await instance.async_init(entry)

        hass.data[DATA][entry.entry_id] = instance
    except Exception as ex:
        exc_type, exc_obj, tb = sys.exc_info()
        line_number = tb.tb_lineno

        _LOGGER.error(f"Failed to async_set_ha, error: {ex}, line: {line_number}")


async def handle_log_level(hass: HomeAssistant, entry: ConfigEntry):
    log_level = entry.options.get(CONF_LOG_LEVEL, LOG_LEVEL_DEFAULT)

    if log_level == LOG_LEVEL_DEFAULT:
        return

    log_level_data = {f"custom_components.{DOMAIN}": log_level.lower()}

    await hass.services.async_call(DOMAIN_LOGGER, SERVICE_SET_LEVEL, log_level_data)
