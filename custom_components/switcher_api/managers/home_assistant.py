"""
Support for Switcher.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switcher/
"""
import logging
import sys
from typing import Optional

from cryptography.fernet import InvalidToken

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity_registry import (
    EntityRegistry,
    async_get_registry as er_async_get_registry,
)
from homeassistant.helpers.event import async_track_time_interval

from ..api.switcher_api import SwitcherApi
from ..helpers.const import *
from ..models.config_data import ConfigData
from .configuration_manager import ConfigManager
from .device_manager import DeviceManager
from .entity_manager import EntityManager

_LOGGER = logging.getLogger(__name__)


class HomeAssistantManager:
    def __init__(self, hass: HomeAssistant):
        self._hass = hass

        self._remove_async_track_time_entities = None
        self._remove_async_track_time_schedule = None
        self._remove_async_track_time_state = None

        self._is_initialized = False
        self._is_updating = False

        self._entity_registry = None

        self._api = None
        self._entity_manager = None
        self._device_manager = None

        self._config_manager = ConfigManager()

        self._integration_name = None

    @property
    def api(self) -> SwitcherApi:
        return self._api

    @property
    def entity_manager(self) -> EntityManager:
        return self._entity_manager

    @property
    def device_manager(self) -> DeviceManager:
        return self._device_manager

    @property
    def entity_registry(self) -> EntityRegistry:
        return self._entity_registry

    @property
    def config_manager(self) -> ConfigManager:
        return self._config_manager

    @property
    def config_data(self) -> Optional[ConfigData]:
        if self._config_manager is not None:
            return self._config_manager.data

        return None

    async def async_init(self, entry: ConfigEntry):
        try:
            _LOGGER.debug("Starting async_init")

            await self._config_manager.update(entry)

            self._integration_name = entry.title

            self._api = SwitcherApi(self._hass, self._config_manager)
            self._entity_manager = EntityManager(self._hass, self)
            self._device_manager = DeviceManager(self._hass, self)

            self._entity_registry = await er_async_get_registry(self._hass)

            self._hass.loop.create_task(self._async_init())
        except InvalidToken:
            error_message = "Encryption key got corrupted, please remove the integration and re-add it"

            _LOGGER.error(error_message)

            await self._hass.services.async_call(
                "persistent_notification",
                "create",
                {"title": DEFAULT_NAME, "message": error_message},
            )

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f"Failed to async_init, error: {ex}, line: {line_number}")

    async def _async_init(self):
        load = self._hass.config_entries.async_forward_entry_setup

        for domain in SIGNALS:
            await load(self._config_manager.config_entry, domain)

        self._is_initialized = True

        await self.async_update_entry()

    def async_update_api(self, now):
        try:
            self._hass.async_create_task(self.api.async_update())
        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(
                f"Failed to create task for update API state @{now}, error: {ex}, line: {line_number}"
            )

    def async_update(self, now):
        try:
            self._hass.async_create_task(self._async_update())
        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(
                f"Failed to create task for update entities @{now}, error: {ex}, line: {line_number}"
            )

    async def _async_update(self):
        if not self._is_initialized:
            _LOGGER.info("NOT INITIALIZED - Failed updating")
            return

        try:
            if self._is_updating:
                _LOGGER.debug("Skip updating")
                return

            _LOGGER.debug("Starting to update")

            self._is_updating = True

            title = self._config_manager.config_entry.title

            if self._integration_name != self._config_manager.config_entry.title:
                renamed = await self._api.set_device_name(title)

                if renamed:
                    self._integration_name = title

            self.device_manager.update()
            self.entity_manager.update()

            self.dispatch_all()
        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f"Failed to async_update, Error: {ex}, Line: {line_number}")

        self._is_updating = False

    async def async_update_entry(self, entry: ConfigEntry = None):
        update_config_manager = entry is not None

        if not update_config_manager:
            entry = self._config_manager.config_entry

            self._remove_async_track_time_state = async_track_time_interval(
                self._hass, self.async_update_api, API_INTERVAL
            )

            self._remove_async_track_time_entities = async_track_time_interval(
                self._hass, self.async_update, UPDATE_INTERVAL
            )

        if not self._is_initialized:
            _LOGGER.info(
                f"NOT INITIALIZED - Failed handling ConfigEntry change: {entry.as_dict()}"
            )
            return

        _LOGGER.info(f"Handling ConfigEntry change: {entry.as_dict()}")

        if update_config_manager:
            await self._config_manager.update(entry)

            state_auto_off = self.api.state.get(KEY_AUTO_OFF)

            current_auto_off = self.config_data.auto_off
            if current_auto_off is None:
                self.config_data.auto_off = state_auto_off

        await self._async_update()

    async def async_remove(self, entry: ConfigEntry):
        _LOGGER.info(f"Removing current integration - {entry.title}")

        if self._remove_async_track_time_entities is not None:
            self._remove_async_track_time_entities()
            self._remove_async_track_time_entities = None

        if self._remove_async_track_time_state is not None:
            self._remove_async_track_time_state()
            self._remove_async_track_time_state = None

        if self._remove_async_track_time_schedule is not None:
            self._remove_async_track_time_schedule()
            self._remove_async_track_time_schedule = None

        unload = self._hass.config_entries.async_forward_entry_unload

        for domain in SUPPORTED_DOMAINS:
            await unload(entry, domain)

        await self._device_manager.async_remove()

        _LOGGER.info(f"Current integration ({entry.title}) removed")

    async def delete_entity(self, domain, name):
        try:
            entity = self.entity_manager.get_entity(domain, name)
            device_name = entity.device_name
            unique_id = entity.unique_id

            self.entity_manager.delete_entity(domain, name)

            device_in_use = self.entity_manager.is_device_name_in_use(device_name)

            entity_id = self.entity_registry.async_get_entity_id(
                domain, DOMAIN, unique_id
            )
            self.entity_registry.async_remove(entity_id)

            if not device_in_use:
                await self.device_manager.delete_device(device_name)
        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(f"Failed to delete_entity, Error: {ex}, Line: {line_number}")

    def dispatch_all(self):
        if not self._is_initialized:
            _LOGGER.info("NOT INITIALIZED - Failed discovering components")
            return

        for domain in SUPPORTED_DOMAINS:
            signal = SIGNALS.get(domain)

            async_dispatcher_send(self._hass, signal)
