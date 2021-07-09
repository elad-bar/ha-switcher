"""
Support for Switcher.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.switcher/
"""
from datetime import timedelta

from homeassistant.components.sensor import DOMAIN as DOMAIN_SENSOR
from homeassistant.components.switch import DOMAIN as DOMAIN_SWITCH
from homeassistant.const import CONF_NAME

CONF_LOG_LEVEL = "log_level"

ENTRY_PRIMARY_KEY = CONF_NAME

CONFIG_FLOW_DATA = "config_flow_data"
CONFIG_FLOW_OPTIONS = "config_flow_options"
CONFIG_FLOW_INIT = "config_flow_init"

VERSION = "1.0.0"

PROTOCOLS = {True: "https", False: "http"}

DOMAIN = "switcher_api"
DATA = f"data_{DOMAIN}"
DATA_API = f"{DATA}_API"
DATA_HA = f"{DATA}_HA"
DATA_HA_ENTITIES = f"{DATA}_HA_Entities"
DEFAULT_NAME = "Switcher API"

CONF_AUTO_OFF = "auto-off"

DOMAIN_LOGGER = "logger"
SERVICE_SET_LEVEL = "set_level"

DEFAULT_ICON = "mdi:alarm-light"

ATTR_FRIENDLY_NAME = "friendly_name"

STATE_INTERVAL = timedelta(seconds=10)
SCHEDULE_INTERVAL = timedelta(minutes=1)
UPDATE_INTERVAL = timedelta(seconds=10)

UPDATE_SIGNAL_SENSOR = f"{DOMAIN}_{DOMAIN_SENSOR}_UPDATE_SIGNAL"
UPDATE_SIGNAL_SWITCH = f"{DOMAIN}_{DOMAIN_SWITCH}_UPDATE_SIGNAL"

SUPPORTED_DOMAINS = [DOMAIN_SWITCH, DOMAIN_SENSOR]
SIGNALS = {
    DOMAIN_SENSOR: UPDATE_SIGNAL_SENSOR,
    DOMAIN_SWITCH: UPDATE_SIGNAL_SWITCH,
}

ENTITY_ID = "id"
ENTITY_NAME = "name"
ENTITY_STATE = "state"
ENTITY_ATTRIBUTES = "attributes"
ENTITY_ICON = "icon"
ENTITY_UNIQUE_ID = "unique-id"
ENTITY_DEVICE_CLASS = "device-class"
ENTITY_DEVICE_NAME = "device-name"
ENTITY_TYPE = "entity-type"
ENTITY_DISABLED = "disabled"
ENTITY_STATUS = "entity-status"
ENTITY_STATUS_EMPTY = None
ENTITY_STATUS_READY = f"{ENTITY_STATUS}-ready"
ENTITY_STATUS_CREATED = f"{ENTITY_STATUS}-created"

SWITCH_MAIN = "main-switch"
SWITCH_SCHEDULE = "schedule-switch"

LOG_LEVEL_DEFAULT = "Default"
LOG_LEVEL_DEBUG = "Debug"
LOG_LEVEL_INFO = "Info"
LOG_LEVEL_WARNING = "Warning"
LOG_LEVEL_ERROR = "Error"

LOG_LEVELS = [
    LOG_LEVEL_DEFAULT,
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARNING,
    LOG_LEVEL_ERROR,
]

KEY_DAYS = "days"
KEY_ENABLED = "enabled"
KEY_END_TIME = "end_time"
KEY_FOUND_SCHEDULES = "found_schedules"
KEY_RECURRING = "recurring"
KEY_SCHEDULES = "schedules"
KEY_SCHEDULE_DATA = "schedule_data"
KEY_SCHEDULE_ID = "schedule_id"
KEY_STATE = "state"
KEY_START_TIME = "start_time"
KEY_SUCCESSFUL = "successful"
KEY_AUTO_OFF = "auto_off"

PARAM_DAYS = "days"
PARAM_HOURS = "hours"
PARAM_MINUTES = "minutes"
PARAM_NAME = "name"
PARAM_SCHEDULE_DATA = "schedule_data"
PARAM_SCHEDULE_ID = "schedule_id"
PARAM_START_HOURS = "start_hours"
PARAM_START_MINUTES = "start_minutes"
PARAM_STOP_HOURS = "stop_hours"
PARAM_STOP_MINUTES = "stop_minutes"

ENDPOINT_GET_STATE = "/switcher/get_state"
ENDPOINT_TURN_ON = "/switcher/turn_on"
ENDPOINT_TURN_OFF = "/switcher/turn_off"
ENDPOINT_SET_AUTO_SHUTDOWN = "/switcher/set_auto_shutdown"
ENDPOINT_SET_DEVICE_NAME = "/switcher/set_device_name"
ENDPOINT_GET_SCHEDULES = "/switcher/get_schedules"
ENDPOINT_ENABLE_SCHEDULE = "/switcher/enable_schedule"
ENDPOINT_DISABLE_SCHEDULE = "/switcher/disable_schedule"
ENDPOINT_DELETE_SCHEDULE = "/switcher/delete_schedule"
ENDPOINT_CREATE_SCHEDULE = "/switcher/create_schedule"
