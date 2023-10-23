"""The MetService NZ data coordinator."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from typing import Any

import aiohttp
import async_timeout
import pytz

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfLength,
    UnitOfSpeed,
    UnitOfVolumetricFlux,
)
from .const import (
    ICON_CONDITION_MAP,
    SENSOR_MAP,
)
import contextlib

_LOGGER = logging.getLogger(__name__)

_RESOURCELOCATION = "/locations/{location}"

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=20)


@dataclass
class WeatherUpdateCoordinatorConfig:
    """Class representing coordinator configuration."""

    api_url: str
    unit_system_api: str
    unit_system: str
    location: str
    location_name: str
    update_interval = MIN_TIME_BETWEEN_UPDATES


class WeatherUpdateCoordinator(DataUpdateCoordinator):
    """The MetService update coordinator."""

    icon_condition_map = ICON_CONDITION_MAP

    def __init__(
        self, hass: HomeAssistant, config: WeatherUpdateCoordinatorConfig
    ) -> None:
        """Initialize."""
        self._hass = hass
        self._api_url = config.api_url
        self._location = config.location
        self._location_name = config.location_name
        self._unit_system_api = config.unit_system_api
        self.unit_system = config.unit_system
        self.data = None
        self._session = async_get_clientsession(self._hass)
        self.units_of_measurement = (
            UnitOfTemperature.CELSIUS,
            UnitOfLength.MILLIMETERS,
            UnitOfLength.METERS,
            UnitOfSpeed.KILOMETERS_PER_HOUR,
            UnitOfPressure.MBAR,
            UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR,
            PERCENTAGE,
        )

        super().__init__(
            hass,
            _LOGGER,
            name="WeatherUpdateCoordinator",
            update_interval=config.update_interval,
        )

    @property
    def location(self):
        """Return the location used for data."""
        return self._location

    @property
    def location_name(self):
        """Return the entity name prefix."""
        return self._location_name

    async def _async_update_data(self) -> dict[str, Any]:
        return await self.get_weather()

    async def get_weather(self):
        """Get weather data."""
        headers = {
            "Accept-Encoding": "gzip",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        }
        try:
            with async_timeout.timeout(10):
                url = f"{self._api_url}/locations/{self.location}"
                response = await self._session.get(url, headers=headers)
                result_current = await response.json(content_type=None)
                if result_current is None:
                    raise ValueError("NO CURRENT RESULT")
                self._check_errors(url, result_current)

            self.data = result_current

            return result_current

        except ValueError as err:
            _LOGGER.error("Check MetService API %s", err.args)
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error("Error fetching MetService data: %s", repr(err))
        _LOGGER.debug(f"MetService data {self.data}")

    def _check_errors(self, url: str, response: dict):
        # _LOGGER.debug(f'Checking errors from {url} in {response}')
        if "errors" not in response:
            return
        if errors := response["errors"]:
            raise ValueError(
                f"Error from {url}: " "; ".join([e["message"] for e in errors])
            )

    def get_current(self, field):
        """Get a specific key from the MetService returned data."""

        def get_from_dict(data_dict, map_list):
            for key in map_list:
                with contextlib.suppress(ValueError):
                    key = int(key)
                try:
                    data_dict = data_dict[key]
                except Exception:
                    data_dict = None
            return data_dict

        keys = SENSOR_MAP[field].split(".")
        result = get_from_dict(self.data, keys)
        return result

    @classmethod
    def _iconcode_to_condition(cls, icon_code):
        for condition, iconcodes in cls.icon_condition_map.items():
            if icon_code in iconcodes:
                return condition
        _LOGGER.warning(
            f'Unmapped iconCode from TWC Api. (44 is Not Available (N/A)) "{icon_code}". '
        )
        return None

    @classmethod
    def _format_timestamp(cls, timestamp_val):
        return datetime.fromisoformat(timestamp_val).astimezone(pytz.utc)
        # return datetime.utcfromtimestamp(timestamp_secs).isoformat("T") + "Z"


class InvalidApiKey(HomeAssistantError):
    """Error to indicate there is an invalid api key."""
