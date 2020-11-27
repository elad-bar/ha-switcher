import logging
import sys
from typing import Dict, List, Optional

from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import EntityRegistry

from ..api.switcher_api import SwitcherApi
from ..helpers.const import *
from ..models.config_data import ConfigData
from ..models.entity_data import EntityData
from .configuration_manager import ConfigManager
from .device_manager import DeviceManager

_LOGGER = logging.getLogger(__name__)


class EntityManager:
    hass: HomeAssistant
    ha = None
    entities: dict
    domain_component_manager: dict
    mqtt_states: dict

    def __init__(self, hass, ha):
        self.hass = hass
        self.ha = ha
        self.domain_component_manager = {}
        self.entities = {}
        self.mqtt_states = {}

    @property
    def entity_registry(self) -> EntityRegistry:
        return self.ha.entity_registry

    @property
    def config_data(self) -> ConfigData:
        return self.ha.config_data

    @property
    def config_manager(self) -> ConfigManager:
        return self.ha.config_manager

    @property
    def api(self) -> SwitcherApi:
        return self.ha.api

    @property
    def device_manager(self) -> DeviceManager:
        return self.ha.device_manager

    @property
    def integration_title(self) -> str:
        return self.config_manager.config_entry.title

    def set_domain_component(self, domain, async_add_entities, component):
        self.domain_component_manager[domain] = {
            "async_add_entities": async_add_entities,
            "component": component,
        }

    def is_device_name_in_use(self, device_name):
        result = False

        for entity in self.get_all_entities():
            if entity.device_name == device_name:
                result = True
                break

        return result

    def get_all_entities(self) -> List[EntityData]:
        entities = []
        for domain in self.entities:
            for name in self.entities[domain]:
                entity = self.entities[domain][name]

                entities.append(entity)

        return entities

    def check_domain(self, domain):
        if domain not in self.entities:
            self.entities[domain] = {}

    def get_entities(self, domain) -> Dict[str, EntityData]:
        self.check_domain(domain)

        return self.entities[domain]

    def get_entity(self, domain, name) -> Optional[EntityData]:
        entities = self.get_entities(domain)
        entity = entities.get(name)

        return entity

    def get_entity_status(self, domain, name):
        entity = self.get_entity(domain, name)

        status = ENTITY_STATUS_EMPTY if entity is None else entity.status

        return status

    def set_entity_status(self, domain, name, status):
        if domain in self.entities and name in self.entities[domain]:
            self.entities[domain][name].status = status

    def delete_entity(self, domain, name):
        if domain in self.entities and name in self.entities[domain]:
            del self.entities[domain][name]

    def set_entity(self, domain, name, data: EntityData):
        try:
            self.check_domain(domain)

            self.entities[domain][name] = data
        except Exception as ex:
            self.log_exception(
                ex, f"Failed to set_entity, domain: {domain}, name: {name}"
            )

    def create_components(self):
        try:
            state = self.api.state
            schedules = self.api.schedules

            self.generate_power_consumption_sensor(state)
            self.generate_electric_current_sensor(state)
            self.generate_main_switch(state)

            if schedules.get(KEY_FOUND_SCHEDULES, False):
                all_schedules = schedules.get(KEY_SCHEDULES, [])

                for schedule in all_schedules:
                    self.generate_schedule_switch(schedule)
        except Exception as ex:
            self.log_exception(ex, "Failed to create_components")

    def update(self):
        self.hass.async_create_task(self._async_update())

    async def _async_update(self):
        step = "Mark as ignore"
        try:
            entities_to_delete = []

            for entity in self.get_all_entities():
                entities_to_delete.append(entity.unique_id)

            step = "Create components"

            self.create_components()

            step = "Start updating"

            for domain in SIGNALS:
                step = f"Start updating domain {domain}"

                entities_to_add = []
                domain_component_manager = self.domain_component_manager[domain]
                domain_component = domain_component_manager["component"]
                async_add_entities = domain_component_manager["async_add_entities"]

                entities = dict(self.get_entities(domain))

                for entity_key in entities:
                    step = f"Start updating {domain} -> {entity_key}"

                    entity = entities[entity_key]

                    entity_id = self.entity_registry.async_get_entity_id(
                        domain, DOMAIN, entity.unique_id
                    )

                    if entity.status == ENTITY_STATUS_CREATED:
                        entity_item = self.entity_registry.async_get(entity_id)

                        if entity.unique_id in entities_to_delete:
                            entities_to_delete.remove(entity.unique_id)

                        step = f"Mark as created - {domain} -> {entity_key}"

                        entity_component = domain_component(
                            self.hass, self.config_manager.config_entry.entry_id, entity
                        )

                        if entity_id is not None:
                            entity_component.entity_id = entity_id

                            state = self.hass.states.get(entity_id)

                            if state is None:
                                restored = True
                            else:
                                restored = state.attributes.get("restored", False)

                                if restored:
                                    _LOGGER.info(
                                        f"Entity {entity.name} restored | {entity_id}"
                                    )

                            if restored:
                                if entity_item is None or not entity_item.disabled:
                                    entities_to_add.append(entity_component)
                        else:
                            entities_to_add.append(entity_component)

                        entity.status = ENTITY_STATUS_READY

                        if entity_item is not None:
                            entity.disabled = entity_item.disabled

                step = f"Add entities to {domain}"

                if len(entities_to_add) > 0:
                    async_add_entities(entities_to_add, True)

            if len(entities_to_delete) > 0:
                _LOGGER.info(f"Following items will be deleted: {entities_to_delete}")

                for domain in SIGNALS:
                    entities = dict(self.get_entities(domain))

                    for entity_key in entities:
                        entity = entities[entity_key]
                        if entity.unique_id in entities_to_delete:
                            await self.ha.delete_entity(domain, entity.name)

        except Exception as ex:
            self.log_exception(ex, f"Failed to update, step: {step}")

    def get_power_consumption_sensor(self, state) -> EntityData:
        entity = None

        try:
            entity_name = f"{self.integration_title} Power Consumption"

            device_name = self.device_manager.get_device_name()

            unique_id = f"{DOMAIN}-{DOMAIN_SENSOR}-{entity_name}"

            state = state.get("power_consumption")
            attributes = {ATTR_FRIENDLY_NAME: entity_name}

            entity = EntityData()

            entity.unique_id = unique_id
            entity.name = entity_name
            entity.state = state
            entity.attributes = attributes
            entity.device_name = device_name
            entity.device_class = "power"
        except Exception as ex:
            self.log_exception(ex, "Failed to get power consumption sensor")

        return entity

    def generate_power_consumption_sensor(self, state):
        try:
            entity = self.get_power_consumption_sensor(state)
            entity_name = entity.name

            self.set_entity(DOMAIN_SENSOR, entity_name, entity)
        except Exception as ex:
            self.log_exception(ex, "Failed to generate power consumption sensor")

    def get_electric_current_sensor(self, state) -> EntityData:
        entity = None

        try:
            entity_name = f"{self.integration_title} Electric Current"

            device_name = self.device_manager.get_device_name()

            unique_id = f"{DOMAIN}-{DOMAIN_SENSOR}-{entity_name}"

            state = state.get("electric_current")
            attributes = {ATTR_FRIENDLY_NAME: entity_name}

            entity = EntityData()

            entity.unique_id = unique_id
            entity.name = entity_name
            entity.state = state
            entity.attributes = attributes
            entity.device_name = device_name
            entity.device_class = "current"
        except Exception as ex:
            self.log_exception(ex, "Failed to get electric current sensor")

        return entity

    def generate_electric_current_sensor(self, state):
        try:
            entity = self.get_electric_current_sensor(state)
            entity_name = entity.name

            self.set_entity(DOMAIN_SENSOR, entity_name, entity)
        except Exception as ex:
            self.log_exception(ex, "Failed to generate electric current sensor")

    def get_main_switch(self, state_data) -> EntityData:
        entity = None

        try:
            device_name = self.device_manager.get_device_name()

            entity_name = f"{self.integration_title}"
            unique_id = f"{DOMAIN}-{DOMAIN_SWITCH}-{entity_name}"

            state = state_data.get(KEY_STATE, STATE_OFF) == STATE_ON

            attributes = {ATTR_FRIENDLY_NAME: entity_name}

            for key in state_data:
                if key not in [KEY_STATE, KEY_SUCCESSFUL]:
                    attributes[key] = state_data[key]

            entity = EntityData()

            entity.unique_id = unique_id
            entity.name = entity_name
            entity.state = state
            entity.attributes = attributes
            entity.icon = "mdi:water-boiler" if state else "mdi:water-boiler-off"
            entity.device_name = device_name
            entity.type = SWITCH_MAIN
        except Exception as ex:
            self.log_exception(ex, "Failed to get main switch")

        return entity

    def generate_main_switch(self, state):
        try:
            entity = self.get_main_switch(state)
            entity_name = entity.name

            self.set_entity(DOMAIN_SWITCH, entity_name, entity)
        except Exception as ex:
            self.log_exception(ex, "Failed to generate main switch")

    def get_schedule_switch(self, schedule_item) -> EntityData:
        entity = None

        try:
            device_name = self.device_manager.get_device_name()
            schedule_id = schedule_item.get(KEY_SCHEDULE_ID)
            schedule_days = schedule_item.get(KEY_DAYS)
            schedule_from = schedule_item.get(KEY_START_TIME)
            schedule_to = schedule_item.get(KEY_END_TIME)
            schedule_recurring = schedule_item.get(KEY_RECURRING)

            schedule_days_full = ", ".join(schedule_days)

            schedule_description = (
                f"{schedule_days_full} - {schedule_from}-{schedule_to}"
            )

            if schedule_recurring:
                schedule_description = f"Recurring - {schedule_description}"

            entity_name = f"{self.integration_title} Schedule #{schedule_id} - {schedule_description}"

            unique_id = f"{DOMAIN}-{DOMAIN_SWITCH}-{entity_name}"

            state = schedule_item.get(KEY_ENABLED, False)

            attributes = {ATTR_FRIENDLY_NAME: entity_name}

            for key in schedule_item:
                if key != KEY_ENABLED:
                    attributes[key] = schedule_item[key]

            entity = EntityData()

            entity.id = schedule_id
            entity.unique_id = unique_id
            entity.name = entity_name
            entity.state = state
            entity.attributes = attributes
            entity.icon = "mdi:camera-timer"
            entity.device_name = device_name
            entity.type = SWITCH_SCHEDULE
        except Exception as ex:
            self.log_exception(ex, "Failed to get main switch")

        return entity

    def generate_schedule_switch(self, schedule_item):
        schedule_id = schedule_item.get(KEY_SCHEDULE_ID)

        try:
            entity = self.get_schedule_switch(schedule_item)
            entity_name = entity.name

            self.set_entity(DOMAIN_SWITCH, entity_name, entity)
        except Exception as ex:
            self.log_exception(ex, f"Failed to generate schedule switch #{schedule_id}")

    @staticmethod
    def log_exception(ex, message):
        exc_type, exc_obj, tb = sys.exc_info()
        line_number = tb.tb_lineno

        _LOGGER.error(f"{message}, Error: {str(ex)}, Line: {line_number}")
