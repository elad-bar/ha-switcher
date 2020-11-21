from homeassistant.exceptions import HomeAssistantError


class AlreadyExistsError(HomeAssistantError):
    title: str

    def __init__(self, title: str):
        self.title = title


class LoginError(HomeAssistantError):
    errors: dict

    def __init__(self, errors):
        self.errors = errors


class AutoOffError(HomeAssistantError):
    title: str

    def __init__(self, time: str, error_code: str):
        self.time = time
        self.error_code = error_code
