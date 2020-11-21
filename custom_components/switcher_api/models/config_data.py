from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SSL

from ..helpers.const import *


class ConfigData:
    name: str
    host: str
    port: int
    is_ssl: bool
    log_level: str

    def __init__(self):
        self.name = DEFAULT_NAME
        self.host = ""
        self.port = DEFAULT_PORT
        self.is_ssl = DEFAULT_IS_SSL
        self.auto_off = None

        self.log_level = LOG_LEVEL_DEFAULT

    def __repr__(self):
        obj = {
            CONF_NAME: self.name,
            CONF_HOST: self.host,
            CONF_PORT: self.port,
            CONF_SSL: self.is_ssl,
            CONF_AUTO_OFF: self.auto_off
        }

        to_string = f"{obj}"

        return to_string

    @property
    def protocol(self):
        protocol = PROTOCOLS[self.is_ssl]

        return protocol
