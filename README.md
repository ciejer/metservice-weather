# MetService New Zealand Weather integration for Home Assistant
View weather data from MetService (NZ), including daily & hourly forecasts, as well as:

* Current condition
* Temperature
* Air pressure & trend
* Humidity
* Wind speed
* Gusts & direction
* UV index
* Pollen levels & type
* Clothes drying times (my reason for creating)
* Tides

## Installation
There are two main ways to install this custom component within your Home Assistant instance.

### HACS (recommended)
1. [Install HACS](https://hacs.xyz/docs/setup/download), if you did not already
2. [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ciejer&repository=metservice-weather&category=integration)
3. Install the MetService New Zealand Weather integration
4. Restart Home Assistant

### Manually
Copy all files in the custom_components/metservice_weather folder to your Home Assistant folder *config/custom_components/metservice_weather*, then restart Home Assistant.

## Getting started
Once installed:

1. Browse to **Configuration**->**Devices & services**
2. Click **+ ADD INTEGRATION**
3. Search for **MetService New Zealand Weather**, then select it
4. Select your location and any other settings (as required)

## Known issues
[See here](https://github.com/ciejer/metservice-weather/issues). I tested about 5 locations and all working, but there's some weirdness around different areas.

## Future enhancements
Please raise an [issue](https://github.com/ciejer/metservice-weather/issues) or [PR](https://github.com/ciejer/metservice-weather/pulls) for anything you'd like added, or any bugs (there will be some)!

## Credits
* [jaydeethree](https://github.com/jaydeethree/Home-Assistant-weatherdotcom) and [alexander0042](https://github.com/alexander0042/pirate-weather-ha/tree/master/custom_components/pirateweather) for their great example to follow for my first HA component
* [natekspencer](https://github.com/natekspencer/hacs-vivint) for the installation / config structure

## Disclaimer
While data is updated every 20 minutes, you should always check the MetService website directly in case of emergency. This integration should never be relied upon for safety of life.
