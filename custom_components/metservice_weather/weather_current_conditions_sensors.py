"""Sensor platform for MetService weather."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast
from collections.abc import Callable
import datetime
from homeassistant.util import dt as dt_util

from .const import (
    FIELD_DESCRIPTION,
    FIELD_HUMIDITY,
    FIELD_PRESSURE,
    FIELD_TEMP,
    FIELD_WINDDIR,
    FIELD_WINDGUST,
    FIELD_WINDSPEED,
    ICON_THERMOMETER,
    ICON_WIND,
)
from homeassistant.components.sensor import (
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfSpeed,
)
from homeassistant.helpers.typing import StateType

import logging
_LOGGER = logging.getLogger(__name__)

AUCKLAND_TIMEZONE = dt_util.get_time_zone("Pacific/Auckland")

@dataclass
class WeatherRequiredKeysMixin:
    """Mixin for required keys."""

    value_fn: Callable[[Any, str], StateType]


@dataclass
class WeatherSensorEntityDescription(SensorEntityDescription, WeatherRequiredKeysMixin):
    """Describes MetService Sensor entity."""

    attr_fn: Callable[[Any], dict[str, Any]] = lambda _: {}
    unit_fn: Callable[[bool], str | None] = lambda _: None


# Helper functions for truncation
def truncate_state(data: Any) -> str:
    """Truncate state to 252 characters and append ellipsis if necessary."""
    if data is None:
        return "No warnings"
    elif isinstance(data, str) and len(data) > 255:
        truncated = f"{data[:252]}..."
        # _LOGGER.info(f"Truncated state: {truncated}")
        return truncated
    elif isinstance(data, str):
        _LOGGER.info(f"State without truncation: {data}")
        return data
    else:
        _LOGGER.info("No warnings available.")
        return "No warnings"


def truncate_attribute(data: Any) -> dict[str, Any]:
    """Truncate warnings attribute to 16,380 characters and append ellipsis if necessary."""
    if isinstance(data, str):
        if len(data) > 16384:
            truncated_attr = {"warnings": f"{data[:16380]}..."}
            # _LOGGER.info(f"Truncated attribute: {truncated_attr}")
            return truncated_attr
        else:
            # _LOGGER.info(f"Attribute without truncation: {data}")
            return {"warnings": data}
    else:
        # _LOGGER.info("No warnings to set in attributes.")
        return {}


current_condition_sensor_descriptions_public = [
    WeatherSensorEntityDescription(
        key="validTimeLocal",
        name="Forecast Description Updated Time",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock",
        value_fn=lambda data, _: datetime.datetime.fromisoformat(data)
        if isinstance(data, str)
        else "Unknown",
    ),
    WeatherSensorEntityDescription(
        key=FIELD_DESCRIPTION,
        name="Weather Description",
        icon="mdi:note-text",
        value_fn=lambda data, _: (
            f"{data[:252]}..." if isinstance(data, str) and len(data) > 255 else (data if data else "No description")
        ),
        # Description can be very long, so truncate to 252 characters and append '...' if necessary
        attr_fn=lambda data: {"full_description": data} if isinstance(data, str) and data else {},
    ),

    WeatherSensorEntityDescription(
        key=FIELD_HUMIDITY,
        name="Relative Humidity",
        icon="mdi:water-percent",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        unit_fn=lambda _: PERCENTAGE,
        value_fn=lambda data, _: cast(int, data) if isinstance(data, (int | float)) else 0,
    ),
    WeatherSensorEntityDescription(
        key="uvIndex",
        name="UV Index",
        icon="mdi:sunglasses",
        value_fn=lambda data, _: cast(str, data) if isinstance(data, str) else "Unknown",
    ),
    WeatherSensorEntityDescription(
        key=FIELD_WINDDIR,
        name="Wind Direction",
        icon=ICON_WIND,
        value_fn=lambda data, _: cast(str, data) if isinstance(data, str) else "Unknown",
    ),
    WeatherSensorEntityDescription(
        key="temperatureFeelsLike",
        name="Temperature - Feels Like",
        icon=ICON_THERMOMETER,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        unit_fn=lambda metric: UnitOfTemperature.CELSIUS
        if metric
        else UnitOfTemperature.FAHRENHEIT,
        value_fn=lambda data, _: cast(float, data) if isinstance(data, (int | float)) else 0.0,
    ),
    WeatherSensorEntityDescription(
        key=FIELD_TEMP,
        name="Temperature",
        icon=ICON_THERMOMETER,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        unit_fn=lambda metric: UnitOfTemperature.CELSIUS
        if metric
        else UnitOfTemperature.FAHRENHEIT,
        value_fn=lambda data, _: cast(float, data) if isinstance(data, (int | float)) else 0.0,
    ),
    WeatherSensorEntityDescription(
        key=FIELD_PRESSURE,
        name="Pressure",
        icon="mdi:gauge",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PRESSURE,
        unit_fn=lambda metric: UnitOfPressure.MBAR if metric else UnitOfPressure.INHG,
        value_fn=lambda data, _: cast(float, data) if isinstance(data, (int | float)) else 0.0,
    ),
    WeatherSensorEntityDescription(
        key=FIELD_WINDGUST,
        name="Wind Gust",
        icon=ICON_WIND,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.WIND_SPEED,
        unit_fn=lambda metric: UnitOfSpeed.KILOMETERS_PER_HOUR
        if metric
        else UnitOfSpeed.MILES_PER_HOUR,
        value_fn=lambda data, _: cast(float, data) if isinstance(data, (int | float)) else 0.0,
    ),
    WeatherSensorEntityDescription(
        key=FIELD_WINDSPEED,
        name="Wind Speed",
        icon=ICON_WIND,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.WIND_SPEED,
        unit_fn=lambda metric: UnitOfSpeed.KILOMETERS_PER_HOUR
        if metric
        else UnitOfSpeed.MILES_PER_HOUR,
        value_fn=lambda data, _: cast(float, data) if isinstance(data, (int | float)) else 0.0,
    ),
    WeatherSensorEntityDescription(
        key="pressureTendencyTrend",
        name="Pressure Tendency Trend",
        icon="mdi:gauge",
        value_fn=lambda data, _: cast(str, data) if isinstance(data, str) else "Unknown",
    ),
    WeatherSensorEntityDescription(
        key="pollen_levels",
        name="Pollen Levels",
        icon="mdi:flower",
        value_fn=lambda data, _: cast(str, data) if isinstance(data, str) else "Unknown",
    ),
    WeatherSensorEntityDescription(
        key="pollen_type",
        name="Pollen Type",
        icon="mdi:flower",
        value_fn=lambda data, _: (
            ". ".join(i.capitalize() for i in data.lstrip(" ").split(". ")[:20])[:255] + ("..." if len(data) > 255 else "")
            if isinstance(data, str)
            else "Unknown"
        ),
        # Pollen Type can be very long, so truncate to 255 characters and capitalize sentences
    ),
    WeatherSensorEntityDescription(
        key="weather_warnings",
        name="MetService Weather Warnings",
        icon="mdi:alert",
        value_fn=lambda data, _: truncate_state(data) if data else "No warnings",
        attr_fn=lambda data: truncate_attribute(data),
    ),
    WeatherSensorEntityDescription(
        key="fire_season",
        name="Fire Season",
        icon="mdi:fire",
        value_fn=lambda data, _: cast(str, data) if isinstance(data, str) else "Unknown",
    ),
    WeatherSensorEntityDescription(
        key="fire_danger",
        name="Fire Danger",
        icon="mdi:fire",
        value_fn=lambda data, _: cast(str, data) if isinstance(data, str) else "Unknown",
    ),
    WeatherSensorEntityDescription(
        key="drying_index_morning",
        name="Clothes Drying Time - Morning",
        icon="mdi:tshirt-crew",
        value_fn=lambda data, _: cast(str, data.replace("Morning: ", "")) if isinstance(data, str) else "Unknown",
    ),
    WeatherSensorEntityDescription(
        key="drying_index_afternoon",
        name="Clothes Drying Time - Afternoon",
        icon="mdi:tshirt-crew",
        value_fn=lambda data, _: cast(str, data.replace("Afternoon: ", "")) if isinstance(data, str) else "Unknown",
    ),
    WeatherSensorEntityDescription(
        key="tides_high",
        name="Next High Tide",
        icon="mdi:beach",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data, _: (
            [
                dt_util.parse_datetime(a["time"])
                for a in data
                if a["type"] == "HIGH"
                and dt_util.parse_datetime(a["time"]) is not None
                and dt_util.parse_datetime(a["time"]) > dt_util.now(AUCKLAND_TIMEZONE)
            ][0]
            if isinstance(data, list) and data else None
        ),
    ),

    WeatherSensorEntityDescription(
        key="tides_low",
        name="Next Low Tide",
        icon="mdi:beach",
        device_class=SensorDeviceClass.TIMESTAMP,

        value_fn=lambda data, _: (
            [
                dt_util.parse_datetime(a["time"])
                for a in data
                if a["type"] == "LOW"
                and dt_util.parse_datetime(a["time"]) is not None
                and dt_util.parse_datetime(a["time"]) > dt_util.now(AUCKLAND_TIMEZONE)
            ][0]
            if isinstance(data, list) and data else None
        ),
    ),
]

current_condition_sensor_descriptions_mobile = [
    WeatherSensorEntityDescription(
        key="validTimeLocal",
        name="Forecast Description Updated Time",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock",
        value_fn=lambda data, _: datetime.datetime.fromisoformat(data)
        if isinstance(data, str)
        else "Unknown",
    ),
    WeatherSensorEntityDescription(
        key=FIELD_DESCRIPTION,
        name="Weather Description",
        icon="mdi:note-text",
        value_fn=lambda data, _: (
            f"{data[:252]}..." if isinstance(data, str) and len(data) > 255 else (data if data else "No description")
        ),
        # Description can be very long, so truncate to 252 characters and append '...' if necessary
        attr_fn=lambda data: {"full_description": data} if isinstance(data, str) and data else {},
    ),
    WeatherSensorEntityDescription(
        key=FIELD_HUMIDITY,
        name="Relative Humidity",
        icon="mdi:water-percent",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        unit_fn=lambda _: PERCENTAGE,
        value_fn=lambda data, _: cast(int, data) if isinstance(data, (int | float)) else 0,
    ),
    WeatherSensorEntityDescription( # UV index from main endpoint is UV Alert from mobile endpoint
        key="uvAlert",
        name="UV Alert",
        icon="mdi:sunglasses",
        value_fn=lambda data, _: cast(str, data) if isinstance(data, str) else "Unknown",
    ),
    WeatherSensorEntityDescription(
        key=FIELD_WINDDIR,
        name="Wind Direction",
        icon=ICON_WIND,
        value_fn=lambda data, _: cast(str, data) if isinstance(data, str) else "Unknown",
    ),
    WeatherSensorEntityDescription(
        key="temperatureFeelsLike",
        name="Temperature - Feels Like",
        icon=ICON_THERMOMETER,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        unit_fn=lambda metric: UnitOfTemperature.CELSIUS
        if metric
        else UnitOfTemperature.FAHRENHEIT,
        value_fn=lambda data, _: cast(float, data) if isinstance(data, (int | float)) else 0.0,
    ),
    WeatherSensorEntityDescription(
        key=FIELD_TEMP,
        name="Temperature",
        icon=ICON_THERMOMETER,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        unit_fn=lambda metric: UnitOfTemperature.CELSIUS
        if metric
        else UnitOfTemperature.FAHRENHEIT,
        value_fn=lambda data, _: cast(float, data) if isinstance(data, (int | float)) else 0.0,
    ),
    WeatherSensorEntityDescription(
        key=FIELD_PRESSURE,
        name="Pressure",
        icon="mdi:gauge",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PRESSURE,
        unit_fn=lambda metric: UnitOfPressure.MBAR if metric else UnitOfPressure.INHG,
        value_fn=lambda data, _: cast(float, data) if isinstance(data, (int | float)) else 0.0,
    ),
    WeatherSensorEntityDescription(
        key=FIELD_WINDGUST,
        name="Wind Gust",
        icon=ICON_WIND,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.WIND_SPEED,
        unit_fn=lambda metric: UnitOfSpeed.KILOMETERS_PER_HOUR
        if metric
        else UnitOfSpeed.MILES_PER_HOUR,
        value_fn=lambda data, _: cast(float, data) if isinstance(data, (int | float)) else 0.0,
    ),
    WeatherSensorEntityDescription(
        key=FIELD_WINDSPEED,
        name="Wind Speed",
        icon=ICON_WIND,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.WIND_SPEED,
        unit_fn=lambda metric: UnitOfSpeed.KILOMETERS_PER_HOUR
        if metric
        else UnitOfSpeed.MILES_PER_HOUR,
        value_fn=lambda data, _: cast(float, data) if isinstance(data, (int | float)) else 0.0,
    ),
    WeatherSensorEntityDescription(
        key="pressureTendencyTrend",
        name="Pressure Tendency Trend",
        icon="mdi:gauge",
        value_fn=lambda data, _: cast(str, data) if isinstance(data, str) else "Unknown",
    ),
    # Pollen is not available from mobile api
    # WeatherSensorEntityDescription(
    #     key="pollen_levels",
    #     name="Pollen Levels",
    #     icon="mdi:flower",
    #     value_fn=lambda data, _: cast(str, data),
    # ),
    # WeatherSensorEntityDescription(
    #     key="pollen_type",
    #     name="Pollen Type",
    #     icon="mdi:flower",
    #     value_fn=lambda data, _: cast(
    #         str, ". ".join(i.capitalize() for i in data.lstrip(" ")[0:254].split(". "))
    #     ),
        # Pollen Type can be very long, so truncate to 254 characters; and capitalize each sentence
    # ),
    WeatherSensorEntityDescription(
        key="drying_index_morning",
        name="Clothes Drying Time - Morning",
        icon="mdi:tshirt-crew",
        value_fn=lambda data, _: cast(str, data.replace("Morning: ", "")) if isinstance(data, str) else "Unknown",
    ),
    WeatherSensorEntityDescription(
        key="drying_index_afternoon",
        name="Clothes Drying Time - Afternoon",
        icon="mdi:tshirt-crew",
        value_fn=lambda data, _: cast(str, data.replace("Afternoon: ", "")) if isinstance(data, str) else "Unknown",
    ),
    WeatherSensorEntityDescription(
        key="weather_warnings",
        name="MetService Weather Warnings",
        icon="mdi:alert",
        value_fn=lambda data, _: truncate_state(data),
        attr_fn=lambda data: truncate_attribute(data),
    ),
    WeatherSensorEntityDescription(
        key="fire_season",
        name="Fire Season",
        icon="mdi:fire",
        value_fn=lambda data, _: cast(str, data) if isinstance(data, str) else "Unknown",
    ),
    WeatherSensorEntityDescription(
        key="fire_danger",
        name="Fire Danger",
        icon="mdi:fire",
        value_fn=lambda data, _: cast(str, data) if isinstance(data, str) else "Unknown",
    ),
    WeatherSensorEntityDescription(
        key="tides_high",
        name="Next High Tide",
        icon="mdi:beach",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data, _: (
            [
                dt_util.parse_datetime(a["time"])
                for a in data
                if a["type"] == "HIGH"
                and dt_util.parse_datetime(a["time"]) is not None
                and dt_util.parse_datetime(a["time"]) > dt_util.now(AUCKLAND_TIMEZONE)
            ][0]
            if isinstance(data, list) and data else None
        ),
    ),

    WeatherSensorEntityDescription(
        key="tides_low",
        name="Next Low Tide",
        icon="mdi:beach",
        device_class=SensorDeviceClass.TIMESTAMP,

        value_fn=lambda data, _: (
            [
                dt_util.parse_datetime(a["time"])
                for a in data
                if a["type"] == "LOW"
                and dt_util.parse_datetime(a["time"]) is not None
                and dt_util.parse_datetime(a["time"]) > dt_util.now(AUCKLAND_TIMEZONE)
            ][0]
            if isinstance(data, list) and data else None
        ),
    ),
]
