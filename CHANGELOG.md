# Changelog

## v1.1.2

- Improved data fetching process

## v1.1.1

- Descriptive error message once switcher failure
- Added missing `iot_class`
- Upgraded `aioswitcher` to v2.0.4

## v1.1.0

#### BREAKING CHANGES:
- Work directly with AIO Switcher, not using switcher_webapi
- If component installed, please remove it and reinstall
- Uses the IP and Device ID instead of API details

## 2020-11-27

- Split entities, API State & API Schedules updates to 3 intervals
- API Schedules will be called once in a minute (instead of every 10 seconds)

## 2020-11-21
Initial version
