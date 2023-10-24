# MetService-Weather Custom Component for Home Assistant

This Custom Component provides MetService NZ connectivity, including forecast, tides, UV, Laundry Drying Times (my reason for creating), and others.
Please raise an issue or PR for anything you'd like added, or any bugs (there will be some! I tested about 5 locations and all working, but there's some weirdness around different areas)

## Installation:
There are two main ways to install this custom component within your Home Assistant instance:
1. Using HACS (see https://hacs.xyz/ for installation instructions if you do not already have it installed):

    1. From within Home Assistant, click on the link to HACS
    2. Click on Integrations
    3. Click on the vertical ellipsis in the top right and select Custom repositories
    4. Enter the URL for this repository `ciejer/metservice-weather` in the section that says _Add custom repository URL_ and select Integration in the Category dropdown list
    5. Click the ADD button
    6. Close the Custom repositories window
    7. You should now be able to see the **MetService New Zealand Weather** card on the HACS Integrations page. Click on INSTALL and proceed with the installation instructions.
    8. Restart your Home Assistant instance and then proceed to the Configuration section below.
2. Manual Installation:
    1. Download or clone this repository.
    2. Copy the contents of the folder `custom_components/metservice_weather` into the same file structure on your Home Assistant instance.
    3. An easy way to do this is using the Samba add-on, but feel free to do so however you want.
    4. Restart your Home Assistant instance and then proceed to the Configuration section below.

## Configuration:
There is a config flow for this MetService integration. After installing the custom component:

1. Go to **Configuration**->**Devices & services**
2. Click **+ ADD INTEGRATION** to setup a new integration
3. Search for **MetService New Zealand Weather** and click on it
4. You will be guided through the rest of the setup process via the config flow


Credit to [jaydeethree](https://github.com/jaydeethree/Home-Assistant-weatherdotcom) and [alexander0042](https://github.com/alexander0042/pirate-weather-ha/tree/master/custom_components/pirateweather) for their great example to follow for my first HA component - and [natekspencer](https://github.com/natekspencer/hacs-vivint) for the installation / config structure.
