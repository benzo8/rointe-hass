# Nexa Preview (non-HACS)

This fork contains Nexa support via WebSocket and is **not HACS-ready**.
It is provided **as-is**, without warranty or support guarantees.

## Important migration note

When you configure this integration for Nexa, Home Assistant will treat it as a
new installation. All devices will get new entity IDs, so you must update any
existing automations, scripts, and dashboards that referenced the old IDs.

# 🌞 rointe-hacs

A minimal integration for Rointe radiators in Home Assistant. 🏡

**Supported Devices**
- Series-D Radiators
- Belize and Olympia Radiators (Nexa support untested)
- Series-D Towel rails
- Oval Towels (Nexa support untested)
- Thermostats

## Features
- Ability to control the temperature
- Provides a sensor with the current temperature, as measured by the device.
- Choose between presets (Eco, Comfort) or Manual Mode
- Notification of firmware updates available
- Energy data (Current power and consumed energy)

## Installation
Please follow these steps:

1. Copy `custom_components/rointe` into your Home Assistant `custom_components` directory.
2. If you previously vendored the SDK, remove any old `custom_components/rointesdk` folder.
3. Restart Home Assistant (it should auto-install the `websocket-client` dependency).
4. Add the integration from Settings -> Devices & Services -> Add Integration -> *Rointe Heaters*.
5. Select **Nexa** as the API type in the config flow.


