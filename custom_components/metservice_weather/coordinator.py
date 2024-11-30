"""The MetService NZ data coordinator."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from typing import Any

import aiohttp
import async_timeout
from homeassistant.util import dt as dt_util

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfLength,
    UnitOfSpeed,
    UnitOfVolumetricFlux,
)

from .const import (
    SENSOR_MAP_MOBILE,
    SENSOR_MAP_PUBLIC,
    RESULTS_CURRENT,
    RESULTS_FORECAST_DAILY,
)

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=20)


@dataclass
class WeatherUpdateCoordinatorConfig:
    """Class representing coordinator configuration."""

    api_url: str
    warnings_url: str
    api_key: str
    api_type: str
    unit_system_api: str
    unit_system: str
    location: str
    location_name: str
    latitude: str
    longitude: str
    enable_tides: bool
    tide_url: str
    update_interval = MIN_TIME_BETWEEN_UPDATES


class WeatherUpdateCoordinator(DataUpdateCoordinator):
    """The MetService update coordinator."""

    def __init__(
        self, hass: HomeAssistant, config: WeatherUpdateCoordinatorConfig
    ) -> None:
        """Initialize."""
        self._hass = hass
        self._api_url = config.api_url
        self._warnings_url = config.warnings_url
        self._api_key = config.api_key
        self._api_type = config.api_type
        self._location = config.location
        self._location_name = config.location_name
        self._latitude = config.latitude
        self._longitude = config.longitude
        self._enable_tides = config.enable_tides
        self._tide_url = config.tide_url
        self._unit_system_api = config.unit_system_api
        self._base_url = 'https://www.metservice.com'
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

    @property
    def api_type(self):
        """Return the API type."""
        return self._api_type

    @property
    def enable_tides(self):
        """Return if tides data is enabled."""
        return self._enable_tides

    @property
    def tide_url(self):
        """Return the tide URL."""
        return self._tide_url

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        if self._api_type == "public":
            return await self.get_public_weather()
        else:
            return await self.get_mobile_weather()

    async def get_mobile_weather(self):
        """Get weather data from mobile API."""
        headers = {
            "Accept": "*/*",
            "User-Agent": "MetServiceNZ/2.19.3 (com.metservice.iphoneapp; build:332; iOS 17.1.1) Alamofire/5.4.3",
            "Accept-Language": "en-CA;q=1.0",
            "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
            "Connection": "keep-alive",
            "apiKey": self._api_key
        }
        try:
            async with async_timeout.timeout(10):
                url = f"{self._api_url}/{self._latitude}/{self._longitude}"
                _LOGGER.info(f"Fetching MetService data from {url}")
                response = await self._session.get(url, headers=headers)
                result_current = await response.json(content_type=None)
                if result_current is None:
                    raise ValueError("No current weather data received.")
                self._check_errors(url, result_current)
            warnings_text = '\n'.join([
                f"{warning['name']}, {warning['markdown']}"
                for warning in result_current['result']['warnings'].get('previews', [])
            ]).replace('**', '').replace('#', '').replace('\n', ' ')
            async with async_timeout.timeout(10):
                url = f"{self._api_url}/locations/{self.location}/7-days"
                response = await self._session.get(url, headers=headers)
                result_daily = await response.json(content_type=None)
                if result_daily is None:
                    raise ValueError("No daily forecast data received.")
                self._check_errors(url, result_daily)
                await self.expand_data_urls(result_current)
                await self.expand_data_urls(result_daily)
            result_current['weather_warnings'] = warnings_text
            result = {}
            if self._enable_tides:
                result_tides = await self.get_tides()
                result_current['tideImport'] = result_tides
                result = {
                    RESULTS_CURRENT: result_current,
                    RESULTS_FORECAST_DAILY: result_daily,
                }
            else:
                result = {
                    RESULTS_CURRENT: result_current,
                    RESULTS_FORECAST_DAILY: result_daily,
                }
            self.data = result
            return result

        except ValueError as err:
            _LOGGER.error("Data validation error: %s", err)
            raise UpdateFailed(f"Data validation error: {err}") from err
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error("Error fetching MetService data: %s", repr(err))
            raise UpdateFailed(f"Error fetching MetService data: {err}") from err
        except Exception as err:
            _LOGGER.error("Unexpected error fetching MetService data: %s", repr(err))
            raise UpdateFailed(f"Unexpected error: {err}") from err
        # finally:
            # _LOGGER.info(f"MetService data updated: {self.data}")

    async def get_public_weather(self):
        """Get weather data from public API."""
        headers = {
            "Accept-Encoding": "gzip",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        }
        try:
            async with async_timeout.timeout(10):
                url = f"{self._api_url}{self.location}"
                _LOGGER.info(f"Fetching MetService data from {url}")
                response = await self._session.get(url, headers=headers)
                _LOGGER.info(f"Received MetService data from {url}: {response}")
                result_current = await response.json(content_type=None)
                _LOGGER.info(f"result_current is: {result_current}")
                if result_current is None:
                    raise ValueError("No current weather data received.")
                self._check_errors(url, result_current)
            await self.expand_data_urls(result_current)
            async with async_timeout.timeout(10):
                url = f"{self._warnings_url}/{result_current['location']['type']}/{result_current['location']['key']}"
                response = await self._session.get(url, headers=headers)
                result_warnings = await response.json(content_type=None)
                if result_warnings is None:
                    raise ValueError("No warnings data received.")
                self._check_errors(url, result_warnings)
                await self.expand_data_urls(result_warnings)
                warnings_text = '\n'.join([
                    f"{warning['name']}, {warning['text']}, {warning['threatPeriod']}"
                    for warning in result_warnings.get('warnings', [])
                ])
            async with async_timeout.timeout(10):
                url = f"{self._api_url}{self.location}/7-days"
                response = await self._session.get(url, headers=headers)
                result_daily = await response.json(content_type=None)
                if result_daily is None:
                    raise ValueError("No daily forecast data received.")
                self._check_errors(url, result_daily)
                await self.expand_data_urls(result_daily)
            result_current['weather_warnings'] = warnings_text
            result = {}
            if self._enable_tides:
                await self.expand_data_urls(result_current)
                await self.expand_data_urls(result_daily)
                result_tides = await self.get_tides()
                result_current['tideImport'] = result_tides
                result = {
                    RESULTS_CURRENT: result_current,
                    RESULTS_FORECAST_DAILY: result_daily,
                }
            else:
                result = {
                    RESULTS_CURRENT: result_current,
                    RESULTS_FORECAST_DAILY: result_daily,
                }
            self.data = result
            return result

        except ValueError as err:
            _LOGGER.error("Data validation error: %s", err)
            raise UpdateFailed(f"Data validation error: {err}") from err
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error("Error fetching MetService data: %s", repr(err))
            raise UpdateFailed(f"Error fetching MetService data: {err}") from err
        except Exception as err:
            _LOGGER.error("Unexpected error fetching MetService data: %s", repr(err))
            raise UpdateFailed(f"Unexpected error: {err}") from err
        # finally:
        #     _LOGGER.info(f"MetService data updated: {self.data}")

    async def get_tides(self):
        """Get tides data."""
        headers = {
            "Accept-Encoding": "gzip",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        }
        try:
            async with async_timeout.timeout(10):
                url = f"{self._tide_url}"
                _LOGGER.info(f"Fetching tides data from {url}")
                response = await self._session.get(url, headers=headers)
                result_tides = await response.json(content_type=None)
                if result_tides is None:
                    raise ValueError("No tides data received.")
                self._check_errors(url, result_tides)
            await self.expand_data_urls(result_tides)
            tide_data = result_tides["layout"]["primary"]["slots"]["main"]["modules"][0]["tideData"]

            return tide_data

        except ValueError as err:
            _LOGGER.error("Data validation error in tides: %s", err)
            raise UpdateFailed(f"Data validation error in tides: {err}") from err
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error("Error fetching tides data: %s", repr(err))
            raise UpdateFailed(f"Error fetching tides data: {err}") from err
        except Exception as err:
            _LOGGER.error("Unexpected error fetching tides data: %s", repr(err))
            raise UpdateFailed(f"Unexpected error in tides: {err}") from err
        # finally:
        #     _LOGGER.info(f"Tides data updated: {tide_data if 'tide_data' in locals() else 'No tides data'}")

    def _check_errors(self, url: str, response: dict):
        """Check for errors in the API response."""
        if "errors" not in response:
            return
        if errors := response["errors"]:
            error_messages = "; ".join([e["message"] for e in errors])
            raise ValueError(f"Error from {url}: {error_messages}")

    def get_from_dict(self, data_dict, map_list):
        """Recursively look for a given key path within a dictionary."""
        if not map_list:
            return data_dict
        if isinstance(data_dict, list):
            for idx, item in enumerate(data_dict):
                if map_list[0].isdigit() and idx == int(map_list[0]):
                    result = self.get_from_dict(item, map_list[1:])
                    if result is not None:
                        return result
                else:
                    result = self.get_from_dict(item, map_list)
                    if result is not None:
                        return result
        elif isinstance(data_dict, dict):
            for key, value in data_dict.items():
                if key == map_list[0]:
                    result = self.get_from_dict(value, map_list[1:])
                    if result is not None:
                        return result
                else:
                    result = self.get_from_dict(value, map_list)
                    if result is not None:
                        return result
        return None

    def get_current_public(self, field):
        """Get a specific key from the MetService returned data."""
        try:
            keys = SENSOR_MAP_PUBLIC[field].split(".")
            result = self.get_from_dict(self.data[RESULTS_CURRENT], keys)
            return result
        except Exception as e:
            _LOGGER.error(f"Error retrieving public sensor '{field}': {e}")
            return None  # Return a dummy value if an error occurs

    def get_current_mobile(self, field):
        """Get a specific key from the MetService returned data."""
        try:
            keys = SENSOR_MAP_MOBILE[field].split(".")
            result = self.get_from_dict(self.data[RESULTS_CURRENT], keys)
            return result
        except Exception as e:
            _LOGGER.error(f"Error retrieving mobile sensor '{field}': {e}")
            return None  # Return a dummy value if an error occurs

    def get_forecast_daily_public(self, field, day):
        """Get a specific key from the MetService returned data."""
        try:
            all_days = self.data[RESULTS_FORECAST_DAILY]["layout"]["primary"]["slots"]["main"]["modules"][0]["days"]
            if field == "":  # send a blank to get the number of days
                return len(all_days)
            this_day = all_days[day]
            keys = SENSOR_MAP_PUBLIC[field].split(".")
            result = self.get_from_dict(this_day, keys)
            return result
        except Exception as e:
            _LOGGER.error(f"Error retrieving public forecast daily sensor '{field}' for day {day}: {e}")
            return None

    def get_forecast_daily_mobile(self, field, day):
        """Get a specific key from the MetService returned data."""
        try:
            all_days = self.data["current"]["result"]["forecastData"]["days"]
            if field == "":  # send a blank to get the number of days
                return len(all_days)
            this_day = all_days[day]
            keys = SENSOR_MAP_MOBILE[field].split(".")
            result = self.get_from_dict(this_day, keys)
            return result
        except Exception as e:
            _LOGGER.error(f"Error retrieving mobile forecast daily sensor '{field}' for day {day}: {e}")
            return None

    @classmethod
    def _format_timestamp(cls, timestamp_val):
        """Format timestamp to ISO format in UTC."""
        return datetime.fromisoformat(timestamp_val).astimezone(dt_util.get_time_zone("UTC")).isoformat()


    async def expand_data_urls(self, data, parent=None, key=None):
        """Recursively expand dataUrl entries in the data, replacing the entire object."""
        if isinstance(data, dict):
            if 'dataUrl' in data:
                url = data['dataUrl']
                if url.startswith('/'):
                    full_url = f"{self._base_url}{url}"
                else:
                    full_url = url
                try:
                    async with async_timeout.timeout(10):
                        response = await self._session.get(full_url)
                        if response.status != 200:
                            _LOGGER.error(f"Error fetching {full_url}: HTTP {response.status}")
                            if parent is not None and key is not None:
                                parent[key] = None  # Handle as needed
                            return
                        result = await response.json(content_type=None)
                    # Replace the entire object containing 'dataUrl' with the fetched data
                    if parent is not None and key is not None:
                        parent[key] = result
                    # Continue processing in case there are nested dataUrls
                    await self.expand_data_urls(result, parent=parent, key=key)
                except Exception as e:
                    _LOGGER.error(f"Error fetching dataUrl {full_url}: {e}")
                    if parent is not None and key is not None:
                        parent[key] = None  # Handle as needed
            else:
                # Recursively process the rest of the dictionary
                for k in list(data.keys()):
                    await self.expand_data_urls(data[k], parent=data, key=k)
        elif isinstance(data, list):
            # Recursively process each item in the list
            for idx, item in enumerate(data):
                await self.expand_data_urls(item, parent=data, key=idx)
        else:
            # Not a dict or list, do nothing
            pass

