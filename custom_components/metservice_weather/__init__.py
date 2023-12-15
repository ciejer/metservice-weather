"""The MetService Weather component."""
import logging
from typing import Final
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_LOCATION,
    CONF_API_KEY,
    Platform,
)
from homeassistant.core import HomeAssistant
from .coordinator import WeatherUpdateCoordinator, WeatherUpdateCoordinatorConfig
from .const import DOMAIN, MOBILE_URL, PUBLIC_URL, API_METRIC, API_URL_METRIC

PLATFORMS: Final = [Platform.WEATHER, Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the MetService Weather component."""
    name = entry.data[CONF_NAME]
    api = entry.data["api"]
    hass.data.setdefault(DOMAIN, {})
    print(api)

    unit_system_api = API_URL_METRIC
    unit_system = API_METRIC

    if api == "public":

        config = WeatherUpdateCoordinatorConfig(
            location=entry.data[CONF_LOCATION],
            location_name=entry.data[CONF_NAME],
            api_type=entry.data["api"],
            latitude = entry.data.get(CONF_LATITUDE, hass.config.latitude),
            longitude = entry.data.get(CONF_LONGITUDE, hass.config.longitude),
            unit_system_api=unit_system_api,
            unit_system=unit_system,
            api_url=PUBLIC_URL,
            api_key='1',
        )

        weathercoordinator = WeatherUpdateCoordinator(hass, config)
        await weathercoordinator.async_config_entry_first_refresh()

        entry.async_on_unload(entry.add_update_listener(_async_update_listener))
        hass.data[DOMAIN][entry.entry_id] = weathercoordinator

        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        return True
    else: # mobile api
        api_key = entry.data[CONF_API_KEY]

        config = WeatherUpdateCoordinatorConfig(
            location=entry.data[CONF_NAME],
            location_name=entry.data[CONF_NAME],
            api_type=entry.data["api"],
            latitude = entry.data.get(CONF_LATITUDE, hass.config.latitude),
            longitude = entry.data.get(CONF_LONGITUDE, hass.config.longitude),
            unit_system_api=unit_system_api,
            unit_system=unit_system,
            api_url=MOBILE_URL,
            api_key=api_key,
        )

        weathercoordinator = WeatherUpdateCoordinator(hass, config)
        await weathercoordinator.async_config_entry_first_refresh()

        entry.async_on_unload(entry.add_update_listener(_async_update_listener))
        hass.data[DOMAIN][entry.entry_id] = weathercoordinator

        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(entry.entry_id)
