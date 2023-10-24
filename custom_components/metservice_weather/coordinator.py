"""The MetService NZ data coordinator."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from typing import Any

import contextlib
import aiohttp
import async_timeout
import pytz

from homeassistant.core import HomeAssistant
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
    SENSOR_MAP,
    RESULTS_CURRENT,
    RESULTS_FORECAST_DAILY,
)

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
            with async_timeout.timeout(10):
                url = f"{self._api_url}/locations/{self.location}/7-days"
                response = await self._session.get(url, headers=headers)
                result_daily = await response.json(content_type=None)
                if result_daily is None:
                    raise ValueError("NO CURRENT RESULT")
                self._check_errors(url, result_daily)
            result = {
                RESULTS_CURRENT: result_current,
                RESULTS_FORECAST_DAILY: result_daily,
            }
            self.data = result

            return result

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

    def get_from_dict(self, data_dict, map_list):
        """Get a value from a dictionary using a list of keys."""
        for key in map_list:
            with contextlib.suppress(ValueError):
                key = int(key)
            try:
                data_dict = data_dict[key]
            except Exception:
                data_dict = None
        return data_dict

    def get_current(self, field):
        """Get a specific key from the MetService returned data."""

        keys = SENSOR_MAP[field].split(".")
        result = self.get_from_dict(self.data[RESULTS_CURRENT], keys)
        return result

    def get_forecast_daily(self, field, day):
        """Get a specific key from the MetService returned data."""
        all_days = self.data[RESULTS_FORECAST_DAILY]["layout"]["primary"]["slots"][
            "main"
        ]["modules"][0]["days"]
        if field == "":  # send a blank to get the number of days
            return len(all_days)
        this_day = all_days[day]
        keys = [SENSOR_MAP[field]]
        if "." in SENSOR_MAP[field]:
            keys = SENSOR_MAP[field].split(".")
        result = self.get_from_dict(
            this_day,
            keys,
        )
        return result

    @classmethod
    def _format_timestamp(cls, timestamp_val):
        return datetime.fromisoformat(timestamp_val).astimezone(pytz.utc)
        # return datetime.utcfromtimestamp(timestamp_secs).isoformat("T") + "Z"
