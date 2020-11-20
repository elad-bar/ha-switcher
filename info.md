# Switcher

## Description

Integration with Switcher V2/V3. 
Creates the following components:

* Sensors - Power Consumption and Electric Current.
* Switch - Main and per schedule

[Changelog](https://github.com/elad-bar/ha-switcher/blob/master/CHANGELOG.md)

## How to

#### Requirements
- Switcher device set up
- Device ID according to the following [manual](https://github.com/NightRang3r/Switcher-V2-Python) by [@NightRang3r](https://github.com/NightRang3r)
- Integration is based on [aioswitcher](https://github.com/TomerFi/aioswitcher) by [@TomerFi](https://github.com/TomerFi)

#### Installations via HACS
Add custom repository `https://github.com/elad-bar/ha-switcher
`
Look for "Switcher" and install


#### Integration settings
###### Basic configuration (Configuration -> Integrations -> Add Switcher)
Fields name | Type | Required | Default | Description
--- | --- | --- | --- | --- |
Host | Texbox | + | None | Hostname or IP address of the Switcher device
Device ID | Textbox | + | 0 | According to the manual above

###### Integration options (Configuration -> Integrations -> Switcher Integration -> Options)  
Fields name | Type | Required | Default | Description
--- | --- | --- | --- | --- |
Log level | Drop-down | + | Default | Changes component's log level (more details below)

**Integration's title**
Initial title will be `Switcher`, once changing the name, it will rename the device name as well

**Log Level's drop-down**
New feature to set the log level for the component without need to set log_level in `customization:` and restart or call manually `logger.set_level` and loose it after restart.

Upon startup or integration's option update, based on the value chosen, the component will make a service call to `logger.set_level` for that component with the desired value,

In case `Default` option is chosen, flow will skip calling the service, after changing from any other option to `Default`, it will not take place automatically, only after restart

###### Configuration validations
Upon submitting the form of creating an integration or updating options,

Component will try to access the device, following errors can appear:
- Switcher integration ({host}) already configured
- Invalid device details - Cannot reach the device
