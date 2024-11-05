"""Support for MetService weather service.

For more details about this platform, please refer to the documentation at
https://github.com/ciejer/metservice-weather.
"""

from . import WeatherUpdateCoordinator
from homeassistant.config_entries import ConfigEntry
from .const import (
    DOMAIN,
    TEMPUNIT,
    LENGTHUNIT,
    SPEEDUNIT,
    PRESSUREUNIT,
    FIELD_CONDITIONS,
    FIELD_HUMIDITY,
    FIELD_PRESSURE,
    FIELD_TEMP,
    FIELD_WINDDIR,
    FIELD_WINDSPEED,
    CONDITION_MAP,
)

import logging
from datetime import datetime

from homeassistant.components.weather import (
    ATTR_FORECAST_PRECIPITATION,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_SPEED,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_CONDITION,
    SingleCoordinatorWeatherEntity,
    WeatherEntityFeature,
    Forecast,
    DOMAIN as WEATHER_DOMAIN,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

ENTITY_ID_FORMAT = WEATHER_DOMAIN + ".{}"

def safe_float(value):
    """Safely convert a value to float, return None if conversion fails."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add weather entity."""
    coordinator: WeatherUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    if(entry.data["api"] == "mobile"):
        async_add_entities(
            [
                MetServiceForecastMobile(coordinator),
            ]
        )
    else:
        async_add_entities(
            [
                MetServiceForecastPublic(coordinator),
            ]
        )


class MetServiceMobile(SingleCoordinatorWeatherEntity):
    """Implementation of a MetService weather service."""

    @property
    def native_temperature(self) -> float:
        """Return the platform temperature in native units (i.e. not converted)."""
        return self.coordinator.get_current_mobile(FIELD_TEMP)

    @property
    def native_temperature_unit(self) -> str:
        """Return the native unit of measurement for temperature."""
        return self.coordinator.units_of_measurement[TEMPUNIT]

    @property
    def native_pressure(self) -> float:
        """Return the pressure in native units."""
        return self.coordinator.get_current_public(FIELD_PRESSURE)

    @property
    def native_pressure_unit(self) -> str:
        """Return the native unit of measurement for pressure."""
        return self.coordinator.units_of_measurement[PRESSUREUNIT]

    @property
    def humidity(self) -> float:
        """Return the relative humidity in native units."""
        return self.coordinator.get_current_public(FIELD_HUMIDITY)

    @property
    def native_wind_speed(self) -> float:
        """Return the wind speed in native units."""
        return self.coordinator.get_current_mobile(FIELD_WINDSPEED)

    @property
    def native_wind_speed_unit(self) -> str:
        """Return the native unit of measurement for wind speed."""
        return self.coordinator.units_of_measurement[SPEEDUNIT]

    @property
    def wind_bearing(self) -> str:
        """Return the wind bearing."""
        return self.coordinator.get_current_mobile(FIELD_WINDDIR)

    @property
    def native_precipitation_unit(self) -> str:
        """Return the native unit of measurement for accumulated precipitation."""
        return self.coordinator.units_of_measurement[LENGTHUNIT]

    @property
    def condition(self) -> str:
        """Return the current condition."""
        if self.coordinator.get_current_mobile(FIELD_CONDITIONS) in CONDITION_MAP:
            return CONDITION_MAP[self.coordinator.get_current_mobile(FIELD_CONDITIONS)]
        return self.coordinator.get_current_mobile(FIELD_CONDITIONS)


class MetServiceForecastMobile(MetServiceMobile):
    """Implementation of a MetService weather forecast."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: WeatherUpdateCoordinator):
        """Initialize the forecast sensor."""
        super().__init__(coordinator)
        self.entity_id = generate_entity_id(
            ENTITY_ID_FORMAT, f"{coordinator.location_name}", hass=coordinator.hass
        )
        self._attr_unique_id = f"{coordinator.location_name},{WEATHER_DOMAIN}".lower()

    @property
    def supported_features(self) -> WeatherEntityFeature:
        """Return the forecast supported features."""
        return (
            WeatherEntityFeature.FORECAST_HOURLY | WeatherEntityFeature.FORECAST_DAILY
        )

    @property
    def name(self):
        """Return the name of the forecast sensor."""
        return f"{self.coordinator.location_name} Forecast"

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return the state attributes."""
        return {
            'forecast_hourly': self.forecast_hourly,
            'forecast_daily': self.forecast_daily
        }

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        """Return hourly forecast."""
        return self.forecast_hourly

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return hourly forecast."""
        return self.forecast_daily

    @property
    def forecast_hourly(self) -> list[Forecast]:
        """Return the hourly forecast in native units."""

        forecast = []
        hourly_readings = self.coordinator.get_current_mobile("hourly_base")
        for hour in range(
            0,
            len(hourly_readings)-1,
            1,
        ):
            this_hour = hourly_readings[hour]

            icon = "sunny"
            rain_fall = safe_float(this_hour.get("rainFall"))
            wind_speed = safe_float(this_hour.get("windSpeed"))
            wind_dir = this_hour.get("windDir")

            if rain_fall is not None and rain_fall > 0:
                # rainy
                if rain_fall > 6:
                    # pouring
                    icon = "pouring"
                else:
                    icon = "rainy"
            else:
                # clear
                if wind_speed is not None and wind_speed > 40:
                    # windy
                    icon = "windy"
                if 7 < datetime.fromisoformat(this_hour["dateISO"]).hour < 19:
                    # daytime
                    icon = "partlycloudy"
                else:
                    # nighttime
                    icon = "clear-night"

            forecast.append(
                Forecast(
                    {
                        ATTR_FORECAST_TEMP: safe_float(this_hour.get("temperature")),
                        ATTR_FORECAST_TIME: self.coordinator._format_timestamp(
                            this_hour["dateISO"]
                        ),
                        ATTR_FORECAST_PRECIPITATION: rain_fall,
                        ATTR_FORECAST_WIND_SPEED: wind_speed,
                        ATTR_FORECAST_WIND_BEARING: wind_dir,
                        ATTR_FORECAST_CONDITION: icon,
                    }
                )
            )
        return forecast

    @property
    def forecast_daily(self) -> list[Forecast]:
        """Return the daily forecast in native units."""

        forecast = []
        num_days = self.coordinator.get_forecast_daily_mobile("", 0)

        for day in range(0, num_days):
            day_condition = self.coordinator.get_forecast_daily_mobile("daily_condition", day)
            if day_condition in CONDITION_MAP:
                day_condition = CONDITION_MAP[day_condition]
            forecast.append(
                Forecast(
                    {
                        ATTR_FORECAST_TEMP: self.coordinator.get_forecast_daily_mobile(
                            "daily_temp_high", day
                        ),
                        ATTR_FORECAST_TEMP_LOW: self.coordinator.get_forecast_daily_mobile(
                            "daily_temp_low", day
                        ),
                        ATTR_FORECAST_CONDITION: day_condition,
                        ATTR_FORECAST_TIME: self.coordinator.get_forecast_daily_mobile("daily_datetime", day),
                    }
                )
            )
        return forecast

class MetServicePublic(SingleCoordinatorWeatherEntity):
    """Implementation of a MetService weather service."""

    @property
    def native_temperature(self) -> float:
        """Return the platform temperature in native units (i.e. not converted)."""
        return self.coordinator.get_current_public(FIELD_TEMP)

    @property
    def native_temperature_unit(self) -> str:
        """Return the native unit of measurement for temperature."""
        return self.coordinator.units_of_measurement[TEMPUNIT]

    @property
    def native_pressure(self) -> float:
        """Return the pressure in native units."""
        return self.coordinator.get_current_public(FIELD_PRESSURE)

    @property
    def native_pressure_unit(self) -> str:
        """Return the native unit of measurement for pressure."""
        return self.coordinator.units_of_measurement[PRESSUREUNIT]

    @property
    def humidity(self) -> float:
        """Return the relative humidity in native units."""
        humidity = self.coordinator.get_current_public(FIELD_HUMIDITY)
        return int(humidity) if humidity is not None else None

    @property
    def native_wind_speed(self) -> float:
        """Return the wind speed in native units."""
        return self.coordinator.get_current_public(FIELD_WINDSPEED)

    @property
    def native_wind_speed_unit(self) -> str:
        """Return the native unit of measurement for wind speed."""
        return self.coordinator.units_of_measurement[SPEEDUNIT]

    @property
    def wind_bearing(self) -> str:
        """Return the wind bearing."""
        return self.coordinator.get_current_public(FIELD_WINDDIR)

    @property
    def native_precipitation_unit(self) -> str:
        """Return the native unit of measurement for accumulated precipitation."""
        return self.coordinator.units_of_measurement[LENGTHUNIT]

    @property
    def condition(self) -> str:
        """Return the current condition."""
        if self.coordinator.get_current_public(FIELD_CONDITIONS) in CONDITION_MAP:
            return CONDITION_MAP[self.coordinator.get_current_public(FIELD_CONDITIONS)]
        return self.coordinator.get_current_public(FIELD_CONDITIONS)


class MetServiceForecastPublic(MetServicePublic):
    """Implementation of a MetService weather forecast."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: WeatherUpdateCoordinator):
        """Initialize the forecast sensor."""
        super().__init__(coordinator)
        self.entity_id = generate_entity_id(
            ENTITY_ID_FORMAT, f"{coordinator.location_name}", hass=coordinator.hass
        )
        self._attr_unique_id = f"{coordinator.location_name},{WEATHER_DOMAIN}".lower()

    @property
    def supported_features(self) -> WeatherEntityFeature:
        """Return the forecast supported features."""
        return (
            WeatherEntityFeature.FORECAST_HOURLY | WeatherEntityFeature.FORECAST_DAILY
        )

    @property
    def name(self):
        """Return the name of the forecast sensor."""
        return f"{self.coordinator.location_name} Forecast"

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return the state attributes."""
        return {
            'forecast_hourly': self.forecast_hourly,
            'forecast_daily': self.forecast_daily
        }


    async def async_forecast_hourly(self) -> list[Forecast] | None:
        """Return hourly forecast."""
        return self.forecast_hourly

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return hourly forecast."""
        return self.forecast_daily

    @property
    def forecast_hourly(self) -> list[Forecast]:
        """Return the hourly forecast in native units."""

        forecast = []
        hourly_readings = self.coordinator.get_current_public("hourly_temp")
        hourly_obs = self.coordinator.get_current_public("hourly_obs")
        hourly_skip = self.coordinator.get_current_public("hourly_skip")
        # print(hourly_readings , hourly_obs, hourly_skip)
        if hourly_obs is None: #Handles regions which do not have daily data
            hourly_obs = self.coordinator.get_current_public("hourly_bkp_obs")

        if hourly_skip is None:
            hourly_skip = self.coordinator.get_current_public("hourly_bkp_skip")

        if hourly_readings is None:
            hourly_readings = self.coordinator.get_current_public("hourly_bkp_temp")
        # print(hourly_readings , hourly_obs, hourly_skip)

        for hour in range(
            hourly_skip,
            hourly_obs + hourly_skip,
            1,
        ):
            this_hour = hourly_readings[hour]

            icon = "sunny"
            rainfall = safe_float(this_hour.get("rainfall"))
            wind_speed = safe_float(this_hour["wind"].get("speed"))
            wind_dir = this_hour["wind"].get("direction")

            if rainfall is not None and rainfall > 0:
                # rainy
                if rainfall > 6:
                    # pouring
                    icon = "pouring"
                else:
                    icon = "rainy"
            else:
                # clear
                if wind_speed is not None and wind_speed > 40:
                    # windy
                    icon = "windy"
                if 7 < datetime.fromisoformat(this_hour["date"]).hour < 19:
                    # daytime
                    icon = "partlycloudy"
                else:
                    # nighttime
                    icon = "clear-night"

            forecast.append(
                Forecast(
                    {
                        ATTR_FORECAST_TEMP: safe_float(this_hour.get("temperature")),
                        ATTR_FORECAST_TIME: self.coordinator._format_timestamp(
                            this_hour["date"]
                        ),
                        ATTR_FORECAST_PRECIPITATION: rainfall,
                        ATTR_FORECAST_WIND_SPEED: wind_speed,
                        ATTR_FORECAST_WIND_BEARING: wind_dir,
                        ATTR_FORECAST_CONDITION: icon,
                    }
                )
            )
        return forecast

    @property
    def forecast_daily(self) -> list[Forecast]:
        """Return the daily forecast in native units."""

        forecast = []
        num_days = self.coordinator.get_forecast_daily_public("", 0)
        for day in range(0, num_days):
            day_condition = self.coordinator.get_forecast_daily_public("daily_condition", day)
            daily_temp_high = self.coordinator.get_forecast_daily_public("daily_temp_high", day)
            daily_temp_low = self.coordinator.get_forecast_daily_public("daily_temp_low", day)
            daily_datetime = self.coordinator.get_forecast_daily_public("daily_datetime", day)
            if daily_temp_high is None: #Rural areas have data in a different location
                daily_temp_high = self.coordinator.get_forecast_daily_public("daily_bkp_temp_high", day)
            if daily_temp_low is None:
                daily_temp_low = self.coordinator.get_forecast_daily_public("daily_bkp_temp_low", day)
            if daily_datetime is None:
                daily_datetime = self.coordinator.get_forecast_daily_public("daily_bkp_datetime", day)
            if day_condition in CONDITION_MAP:
                day_condition = CONDITION_MAP[day_condition]
            forecast.append(
                Forecast(
                    {
                        ATTR_FORECAST_TEMP: daily_temp_high,
                        ATTR_FORECAST_TEMP_LOW: daily_temp_low,
                        ATTR_FORECAST_CONDITION: day_condition,
                        ATTR_FORECAST_TIME: daily_datetime,
                    }
                )
            )
        return forecast

