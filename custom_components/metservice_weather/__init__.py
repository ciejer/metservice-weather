"""The MetService Weather component."""
import logging
from typing import Final
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    CONF_LOCATION,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.util.unit_system import METRIC_SYSTEM
from .coordinator import WeatherUpdateCoordinator, WeatherUpdateCoordinatorConfig
from .const import DOMAIN, API_URL, API_METRIC, API_URL_METRIC

PLATFORMS: Final = [Platform.WEATHER, Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the MetService Weather component."""
    hass.data.setdefault(DOMAIN, {})

    unit_system_api = API_URL_METRIC
    unit_system = API_METRIC
    config = WeatherUpdateCoordinatorConfig(
        location=entry.data[CONF_LOCATION],
        location_name=entry.data[CONF_NAME],
        unit_system_api=unit_system_api,
        unit_system=unit_system,
        api_url=API_URL,
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
