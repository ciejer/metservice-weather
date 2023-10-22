# MetService-Weather

Metservice New Zealand Weather Home Assistant Custom Component

[![metservice-weather](https://img.shields.io/github/v/release/ciejer/metservice-weather)](https://github.com/ciejer/metservice-weather/releases/latest) [![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration) ![Maintenance](https://img.shields.io/maintenance/yes/2023.svg) [![metservice-weather_downloads](https://img.shields.io/github/downloads/ciejer/metservice-weather/total)](https://github.com/ciejer/metservice-weather)

# metservice-weather Integration for Home Assistant

_Work in progress_

Known limitations: There is only limited error and exception handling in this pre-release.

This integration will represent .......

## Installation

Make sure you have the credentials available for your account with metservice-weather cloud.

### Preferred download method

- Use HACS, add this repo as a custom repository and install metservice-weather integration.
- Restart Home Assistant

### Manual download method

- Copy all files from custom_components/metservice-weather in this repo to your config custom_components/metservice-weather
- Restart Home Assistant

### Setup

Request a client_id and client_secret from the manufacturer and
enter following lines to `configuration.yaml`

```yaml
metservice-weather:
  client_id: your_client_id
  client_secret: your_client_secret
```

Goto Integrations->Add and select metservice-weather

Follow instructions to authenticate with metservice-weather cloud server. Allow full access for Home Assistant client.

## Disclaimer

The package and its author are not affiliated with metservice-weather. Use at your own risk.

## License

The package is released under the MIT license.
