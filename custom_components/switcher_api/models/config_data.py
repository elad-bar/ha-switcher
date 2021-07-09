from homeassistant.const import CONF_DEVICE_ID, CONF_IP_ADDRESS

from ..helpers.const import *


class ConfigData:
    name: str
    ip_address: str
    device_id: str
    log_level: str

    def __init__(self):
        self.name = DEFAULT_NAME
        self.ip_address = ""
        self.device_id = ""
        self.auto_off = None

        self.log_level = LOG_LEVEL_DEFAULT

    def __repr__(self):
        obj = {
            CONF_NAME: self.name,
            CONF_IP_ADDRESS: self.ip_address,
            CONF_DEVICE_ID: self.device_id,
            CONF_AUTO_OFF: self.auto_off,
        }

        to_string = f"{obj}"

        return to_string
