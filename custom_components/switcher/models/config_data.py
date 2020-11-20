from homeassistant.const import CONF_HOST

from ..helpers.const import *


class ConfigData:
    name: str
    host: str
    phone_id: str
    device_id: str
    device_password: str
    log_level: str

    def __init__(self):
        self.name = DEFAULT_NAME
        self.host = ""
        self.phone_id = DEFAULT_PHONE_ID
        self.device_id = DEFAULT_DEVICE_ID
        self.device_password = DEFAULT_DEVICE_PASSWORD

        self.log_level = LOG_LEVEL_DEFAULT

    def __repr__(self):
        obj = {
            CONF_NAME: self.name,
            CONF_HOST: self.host,
            CONF_DEVICE_ID: self.device_id,
        }

        to_string = f"{obj}"

        return to_string
