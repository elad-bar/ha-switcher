# Switcher API

## Description

Integration with Switcher API. 
Creates the following components:

* Sensors - Power Consumption and Electric Current.
* Switch - Main and per schedule

[Changelog](https://github.com/elad-bar/ha-switcher/blob/master/CHANGELOG.md)

## How to

#### Requirements
- Switcher device 
- Switcher API docker [switcher_webapi](https://github.com/TomerFi/switcher_webapi) by [@TomerFi](https://github.com/TomerFi)

#### Installations via HACS
Add custom repository `https://github.com/elad-bar/ha-switcher`

Look for "Switcher API" and install


#### Integration settings
###### Basic configuration (Configuration -> Integrations -> Add Switcher)
Fields name | Type | Required | Default | Description
--- | --- | --- | --- | --- |
Host | Textbox | + | None | Hostname or IP address of the Switcher API
Post | Textbox | + | 8000 | Port of the Switcher API
SSL | Checkbox | + | False | Whether the Switcher API is using SSL (HTTPS) or not 

###### Integration options (Configuration -> Integrations -> Switcher Integration -> Options)  
Fields name | Type | Required | Default | Description
--- | --- | --- | --- | --- |
Log level | Drop-down | + | Default | Changes component's log level (more details below)
Auto off interval | Textbox | + | According to Switcher Device | Changes the auto-off interval (between 01:00:00 to 03:00:00)

**Integration's title**
Initial title will be `Switcher`, once changing the name, it will rename the device name as well

**Log Level's drop-down**
New feature to set the log level for the component without need to set log_level in `customization:` and restart or call manually `logger.set_level` and loose it after restart.

Upon startup or integration's option update, based on the value chosen, the component will make a service call to `logger.set_level` for that component with the desired value,

In case `Default` option is chosen, flow will skip calling the service, after changing from any other option to `Default`, it will not take place automatically, only after restart

###### Configuration errors
####### Setup new integration
 
- Switcher API is already configured
- Invalid Switcher API details

####### Edit options

- Auto-off interval below minimum, must be between 01:00:00 to 03:00:00 minutes
- Auto-off interval above maximum, must be between 01:00:00 to 03:00:00 minutes