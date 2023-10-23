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

from homeassistant.components.weather import (
    ATTR_FORECAST_PRECIPITATION,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_SPEED,
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


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add weather entity."""
    coordinator: WeatherUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            MetServiceForecast(coordinator),
        ]
    )


class MetService(SingleCoordinatorWeatherEntity):
    """Implementation of a MetService weather service."""

    @property
    def native_temperature(self) -> float:
        """Return the platform temperature in native units (i.e. not converted)."""
        return self.coordinator.get_current(FIELD_TEMP)

    @property
    def native_temperature_unit(self) -> str:
        """Return the native unit of measurement for temperature."""
        return self.coordinator.units_of_measurement[TEMPUNIT]

    @property
    def native_pressure(self) -> float:
        """Return the pressure in native units."""
        return self.coordinator.get_current(FIELD_PRESSURE)

    @property
    def native_pressure_unit(self) -> str:
        """Return the native unit of measurement for pressure."""
        return self.coordinator.units_of_measurement[PRESSUREUNIT]

    @property
    def humidity(self) -> float:
        """Return the relative humidity in native units."""
        return self.coordinator.get_current(FIELD_HUMIDITY)

    @property
    def native_wind_speed(self) -> float:
        """Return the wind speed in native units."""
        return self.coordinator.get_current(FIELD_WINDSPEED)

    @property
    def native_wind_speed_unit(self) -> str:
        """Return the native unit of measurement for wind speed."""
        return self.coordinator.units_of_measurement[SPEEDUNIT]

    @property
    def wind_bearing(self) -> str:
        """Return the wind bearing."""
        return self.coordinator.get_current(FIELD_WINDDIR)

    @property
    def native_precipitation_unit(self) -> str:
        """Return the native unit of measurement for accumulated precipitation."""
        return self.coordinator.units_of_measurement[LENGTHUNIT]

    @property
    def condition(self) -> str:
        """Return the current condition."""
        if self.coordinator.get_current(FIELD_CONDITIONS) in CONDITION_MAP:
            return CONDITION_MAP[self.coordinator.get_current(FIELD_CONDITIONS)]
        return self.coordinator.get_current(FIELD_CONDITIONS)


class MetServiceForecast(MetService):
    """Implementation of a MetService weather forecast."""

    def __init__(self, coordinator: WeatherUpdateCoordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_id = generate_entity_id(
            ENTITY_ID_FORMAT, f"{coordinator.location}", hass=coordinator.hass
        )
        self._attr_unique_id = f"{coordinator.location},{WEATHER_DOMAIN}".lower()

    @property
    def supported_features(self) -> WeatherEntityFeature:
        """Return the forecast supported features."""
        return WeatherEntityFeature.FORECAST_HOURLY

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        """Return hourly forecast."""
        return self.forecast_hourly

    @property
    def forecast_hourly(self) -> list[Forecast]:
        """Return the hourly forecast in native units."""

        forecast = []
        hourly_readings = self.coordinator.get_current("hourly_temp")
        for hour in range(
            self.coordinator.get_current("hourly_skip"),
            self.coordinator.get_current("hourly_obs")
            + self.coordinator.get_current("hourly_skip"),
            1,
        ):
            this_hour = hourly_readings[hour]
            forecast.append(
                Forecast(
                    {
                        # ATTR_FORECAST_CLOUD_COVERAGE: self.coordinator.get_forecast_daily(
                        #     FIELD_CLOUD_COVER, hour
                        # ),
                        # ATTR_FORECAST_PRECIPITATION: self.coordinator.get_forecast_hourly(
                        #     FIELD_QPF, hour
                        # ),
                        # ATTR_FORECAST_PRECIPITATION_PROBABILITY: self.coordinator.get_forecast_hourly(
                        #     FIELD_PRECIPCHANCE, hour
                        # ),
                        ATTR_FORECAST_TEMP: this_hour["temperature"],
                        ATTR_FORECAST_TIME: self.coordinator._format_timestamp(
                            this_hour["date"]
                        ),
                        ATTR_FORECAST_PRECIPITATION: this_hour["rainfall"],
                        ATTR_FORECAST_WIND_SPEED: this_hour["wind"]["speed"],
                        # ATTR_FORECAST_TEMP: self.coordinator.get_forecast_hourly(
                        #     FIELD_TEMP, hour
                        # ),
                        # ATTR_FORECAST_TIME: self.coordinator._format_timestamp(
                        #     self.coordinator.get_forecast_hourly(
                        #         FIELD_VALIDTIMEUTC, hour
                        #     )
                        # ),
                        # ATTR_FORECAST_WIND_SPEED: self.coordinator.get_forecast_hourly(
                        #     FIELD_WINDSPEED, hour
                        # ),
                    }
                )
            )
        return forecast
