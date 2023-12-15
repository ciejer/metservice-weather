"""Support for MetService weather service.

For more details about this platform, please refer to the documentation at
https://github.com/ciejer/metservice-weather.
"""

from typing import Final


DOMAIN = "metservice_weather"
CONF_ATTRIBUTION = "Data provided by the MetService NZ weather service"

FIELD_DESCRIPTION = "wxPhraseLong"
FIELD_HUMIDITY = "relativeHumidity"
FIELD_PRESSURE = "pressureAltimeter"
FIELD_TEMP = "temperature"
FIELD_WINDDIR = "windDirection"
FIELD_WINDGUST = "windGust"
FIELD_WINDSPEED = "windSpeed"
FIELD_CONDITIONS = "condition"


SENSOR_MAP_MOBILE: Final[dict[str, str]] = {
    "pollen_levels": "layout.primary.slots.left-minor.modules.4.pollen.pollenLevels.level",
    "pollen_type": "layout.primary.slots.left-minor.modules.4.pollen.pollenLevels.type",
    "drying_index_morning": "result.genericModules.0.sections.0.paragraphs.0.lines.0.markdown",
    "drying_index_afternoon": "result.genericModules.0.sections.0.paragraphs.0.lines.1.markdown",
    FIELD_TEMP: "result.observationData.temperature",
    FIELD_HUMIDITY: "result.observationData.relativeHumidity",
    FIELD_PRESSURE: "result.observationData.pressure",
    FIELD_WINDDIR: "result.observationData.windDirection",
    FIELD_WINDSPEED: "result.observationData.windSpeed",
    FIELD_WINDGUST: "result.observationData.windGustSpeed",
    FIELD_CONDITIONS: "result.forecastData.days.0.forecastWord",
    FIELD_DESCRIPTION: "result.forecastData.days.0.forecast",
    "validTimeLocal": "result.forecastData.days.0.issuedAtISO",
    "uvAlert": "result.forecastData.days.0.uvHasAlert",
    "temperatureFeelsLike": "layout.primary.slots.left-major.modules.0.observations.temperature.0.feelsLike",
    "pressureTendencyTrend": "result.observationData.pressureTrend",
    "location_name": "location.label",
    "hourly_temp": "layout.primary.slots.main.modules.2.graph.columns",
    "hourly_timestamp": "layout.primary.slots.main.modules.2.graph.columns",
    "hourly_skip": "layout.primary.slots.main.modules.2.graph.series.0.count",
    "hourly_obs": "layout.primary.slots.main.modules.2.graph.series.1.count",
    "tides_high": "result.tides.0.days",
    "tides_low": "result.tides.0.days",
    "daily_base": "layout.primary.slots.main.modules.0.days",
    "daily_temp_high": "forecasts.0.highTemp",
    "daily_temp_low": "forecasts.0.lowTemp",
    "daily_condition": "condition",
    "daily_datetime": "date",
}


SENSOR_MAP_PUBLIC: Final[dict[str, str]] = {
    "pollen_levels": "layout.primary.slots.left-minor.modules.4.pollen.pollenLevels.level",
    "pollen_type": "layout.primary.slots.left-minor.modules.4.pollen.pollenLevels.type",
    "drying_index_morning": "layout.primary.slots.left-minor.modules.4.dryingIndex.dryingState.0.text",
    "drying_index_afternoon": "layout.primary.slots.left-minor.modules.4.dryingIndex.dryingState.1.text",
    FIELD_TEMP: "layout.primary.slots.left-major.modules.0.observations.temperature.0.current",
    FIELD_HUMIDITY: "layout.primary.slots.left-major.modules.0.observations.rain.0.relativeHumidity",
    FIELD_PRESSURE: "layout.primary.slots.left-major.modules.0.observations.pressure.0.atSeaLevel",
    FIELD_WINDDIR: "layout.primary.slots.left-major.modules.0.observations.wind.0.direction",
    FIELD_WINDSPEED: "layout.primary.slots.left-major.modules.0.observations.wind.0.averageSpeed",
    FIELD_WINDGUST: "layout.primary.slots.left-major.modules.0.observations.wind.0.gustSpeed",
    FIELD_CONDITIONS: "layout.primary.slots.main.modules.0.days.0.condition",
    FIELD_DESCRIPTION: "layout.primary.slots.main.modules.0.days.0.forecasts.0.statement",
    "validTimeLocal": "layout.primary.slots.main.modules.0.days.0.issuedAt",
    "uvIndex": "layout.primary.slots.left-minor.modules.4.uv.sunProtection.uvAlertLevel",
    "temperatureFeelsLike": "layout.primary.slots.left-major.modules.0.observations.temperature.0.feelsLike",
    "pressureTendencyTrend": "layout.primary.slots.left-major.modules.0.observations.pressure.0.trend",
    "location_name": "location.label",
    "hourly_temp": "layout.primary.slots.main.modules.2.graph.columns",
    "hourly_timestamp": "layout.primary.slots.main.modules.2.graph.columns",
    "hourly_skip": "layout.primary.slots.main.modules.2.graph.series.0.count",
    "hourly_obs": "layout.primary.slots.main.modules.2.graph.series.1.count",
    "tides_high": "layout.secondary.slots.major.modules.1.tideData",
    "tides_low": "layout.secondary.slots.major.modules.1.tideData",
    "daily_base": "layout.primary.slots.main.modules.0.days",
    "daily_temp_high": "forecasts.0.highTemp",
    "daily_temp_low": "forecasts.0.lowTemp",
    "daily_condition": "condition",
    "daily_datetime": "date",
}

CONDITION_MAP: Final[dict[str, str]] = {
    # Every newly detected entry should be added to this list, mapping to homeassistant's supported values from below.
    # These initial entries are as found on https://about.metservice.com/our-company/learning-centre/weather-icons-explained/
    "cloudy": "cloudy",
    "drizzle": "rainy",
    "few-showers": "rainy",
    "few-showers-night": "rainy",
    "fine": "sunny",
    "fog": "fog",
    "frost": "clear-night",
    "hail": "hail",
    "mostly-cloudy": "cloudy",
    "partly-cloudy": "partlycloudy",
    "partly-cloudy-night": "partlycloudy",
    "rain": "pouring",
    "showers": "rainy",
    "snow": "snowy",
    "thunder": "lightning",
    "wind-rain": "exceptional",
    "windy": "windy"
}

LOCATIONS = [
    {"label": "Dargaville", "value": "dargaville"},
    {"label": "Kaikohe", "value": "kaikohe"},
    {"label": "Kaitaia", "value": "kaitaia"},
    {"label": "Kaitaia Airport", "value": "kaitaia-airport"},
    {"label": "Kerikeri", "value": "kerikeri"},
    {"label": "Paihia", "value": "paihia"},
    {"label": "Whangārei", "value": "whangarei"},
    {"label": "Auckland Central", "value": "auckland"},
    {"label": "Hunua", "value": "hunua"},
    {"label": "Kumeu", "value": "kumeu"},
    {"label": "Manukau", "value": "manukau"},
    {"label": "North Shore", "value": "north-shore"},
    {"label": "Pukekohe", "value": "pukekohe"},
    {"label": "Waiheke Island", "value": "waiheke-island"},
    {"label": "Waitakere", "value": "waitakere"},
    {"label": "Warkworth", "value": "warkworth"},
    {"label": "Hamilton", "value": "hamilton"},
    {"label": "Matamata", "value": "matamata"},
    {"label": "Paeroa", "value": "paeroa"},
    {"label": "Te Awamutu", "value": "te-awamutu"},
    {"label": "Tokoroa", "value": "tokoroa"},
    {"label": "Te Kuiti", "value": "te-kuiti"},
    {"label": "Thames", "value": "thames"},
    {"label": "Whitianga", "value": "whitianga"},
    {"label": "Rotorua", "value": "rotorua"},
    {"label": "Tauranga", "value": "tauranga"},
    {"label": "Te Puke", "value": "te-puke"},
    {"label": "Whakatāne", "value": "whakatane"},
    {"label": "Taupō", "value": "taupo"},
    {"label": "Taupō Airport", "value": "taupo-airport"},
    {"label": "Gisborne", "value": "gisborne"},
    {"label": "Ruatoria", "value": "ruatoria"},
    {"label": "Eastern Rangitaiki", "value": "eastern-rangitaiki"},
    {"label": "Hastings", "value": "hastings"},
    {"label": "Mahia", "value": "mahia"},
    {"label": "Napier", "value": "napier"},
    {"label": "Napier Airport", "value": "napier-airport"},
    {"label": "Waipukurau", "value": "waipukurau"},
    {"label": "Wairoa", "value": "wairoa"},
    {"label": "Hāwera", "value": "hawera"},
    {"label": "New Plymouth", "value": "new-plymouth"},
    {"label": "New Plymouth Airport", "value": "new-plymouth-airport"},
    {"label": "Taumarunui", "value": "taumarunui"},
    {"label": "Waiouru", "value": "waiouru"},
    {"label": "Whanganui", "value": "wanganui"},
    {"label": "Whanganui Airport", "value": "wanganui-airport"},
    {"label": "Ohakea", "value": "ohakea"},
    {"label": "Palmerston North", "value": "palmerston-north"},
    {"label": "Palmerston North Airport", "value": "palmerston-north-airport"},
    {"label": "Castlepoint", "value": "castlepoint"},
    {"label": "Dannevirke", "value": "dannevirke"},
    {"label": "Martinborough", "value": "martinborough"},
    {"label": "Masterton", "value": "masterton"},
    {"label": "Levin", "value": "levin"},
    {"label": "Paraparaumu", "value": "paraparaumu"},
    {"label": "Te Horo", "value": "te-horo"},
    {"label": "Waikanae", "value": "waikanae"},
    {"label": "Ōtaki", "value": "otaki"},
    {"label": "Judgeford", "value": "judgeford"},
    {"label": "Lower Hutt", "value": "lower-hutt"},
    {"label": "Lyall Bay", "value": "lyall-bay"},
    {"label": "Ohariu Valley", "value": "ohariu-valley"},
    {"label": "Porirua", "value": "porirua"},
    {"label": "Upper Hutt", "value": "upper-hutt"},
    {"label": "Wainuiomata", "value": "wainuiomata"},
    {"label": "Wellington Central", "value": "wellington"},
    {"label": "Blenheim", "value": "blenheim"},
    {"label": "Kaikōura", "value": "kaikoura"},
    {"label": "Kaikōura Airport", "value": "kaikoura-airport"},
    {"label": "Picton", "value": "picton"},
    {"label": "Motueka", "value": "motueka"},
    {"label": "Nelson", "value": "nelson"},
    {"label": "Takaka", "value": "takaka"},
    {"label": "Reefton", "value": "reefton"},
    {"label": "Westport", "value": "westport"},
    {"label": "Franz Josef", "value": "franz-josef"},
    {"label": "Greymouth", "value": "greymouth"},
    {"label": "Haast", "value": "haast"},
    {"label": "Hokitika", "value": "hokitika"},
    {"label": "Ashburton", "value": "ashburton"},
    {"label": "Darfield", "value": "darfield"},
    {"label": "Methven", "value": "methven"},
    {"label": "Rakaia", "value": "rakaia"},
    {"label": "Timaru", "value": "timaru"},
    {"label": "Waipara", "value": "waipara"},
    {"label": "Culverden", "value": "culverden"},
    {"label": "Mount Cook", "value": "mount-cook"},
    {"label": "Omarama", "value": "omarama"},
    {"label": "Twizel", "value": "twizel"},
    {"label": "Banks Peninsula", "value": "banks-peninsula"},
    {"label": "Christchurch Central", "value": "christchurch"},
    {"label": "Eastern Suburbs", "value": "eastern-suburbs"},
    {"label": "Hilltop", "value": "hill-top"},
    {"label": "Lincoln", "value": "lincoln"},
    {"label": "Marshland", "value": "marshlands"},
    {"label": "Port Hills", "value": "port-hills"},
    {"label": "Oamaru", "value": "oamaru"},
    {"label": "Oamaru Airport", "value": "oamaru-airport"},
    {"label": "Alexandra", "value": "alexandra"},
    {"label": "Dunedin", "value": "dunedin"},
    {"label": "Middlemarch", "value": "middlemarch"},
    {"label": "Mosgiel", "value": "mosgiel"},
    {"label": "Waitati", "value": "waitati"},
    {"label": "Nugget Point", "value": "nugget-point"},
    {"label": "Queenstown", "value": "queenstown"},
    {"label": "Wānaka", "value": "wanaka"},
    {"label": "Gore", "value": "gore"},
    {"label": "Invercargill", "value": "invercargill"},
    {"label": "Lumsden", "value": "lumsden"},
    {"label": "Milford Sound", "value": "milford-sound"},
    {"label": "Stewart Island", "value": "stewart-island"},
    {"label": "Te Anau", "value": "te-anau"},
]


PUBLIC_URL = "https://www.metservice.com/publicData/webdata/towns-cities"
MOBILE_URL = "https://api.metservice.com/mobile/nz/weatherData"
API_METRIC: Final = "metric"
API_URL_METRIC: Final = "m"
DEFAULT_LOCATION = "tauranga"

TEMPUNIT = 0
LENGTHUNIT = 1
SPEEDUNIT = 3
PRESSUREUNIT = 4

RESULTS_CURRENT = "current"
RESULTS_FORECAST_DAILY = "daily"
RESULTS_FORECAST_HOURLY = "hourly"

ICON_THERMOMETER = "mdi:thermometer"
ICON_WIND = "mdi:weather-windy"
