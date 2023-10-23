"""Support for MetService weather service.

For more details about this platform, please refer to the documentation at
https://github.com/ciejer/metservice-weather.
"""

from typing import Final

from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_EXCEPTIONAL,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_HAIL,
    ATTR_CONDITION_LIGHTNING,
    ATTR_CONDITION_LIGHTNING_RAINY,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SNOWY_RAINY,
    ATTR_CONDITION_SUNNY,
    ATTR_CONDITION_WINDY,
    ATTR_CONDITION_WINDY_VARIANT,
)

DOMAIN = "metservice_weather"
CONF_ATTRIBUTION = "Data provided by the MetService NZ weather service"
CONF_LANG = "lang"

ENTRY_WEATHER_COORDINATOR = "weather_coordinator"

# Language Supported Codes
LANG_CODES = [
    "am-ET",
    "ar-AE",
    "az-AZ",
    "bg-BG",
    "bn-BD",
    "bn-IN",
    "bs-BA",
    "ca-ES",
    "cs-CZ",
    "da-DK",
    "de-DE",
    "el-GR",
    "en-GB",
    "en-IN",
    "en-US",
    "es-AR",
    "es-ES",
    "es-LA",
    "es-MX",
    "es-UN",
    "es-US",
    "et-EE",
    "fa-IR",
    "fi-FI",
    "fr-CA",
    "fr-FR",
    "gu-IN",
    "he-IL",
    "hi-IN",
    "hr-HR",
    "hu-HU",
    "in-ID",
    "is-IS",
    "it-IT",
    "iw-IL",
    "ja-JP",
    "jv-ID",
    "ka-GE",
    "kk-KZ",
    "km-KH",
    "kn-IN",
    "ko-KR",
    "lo-LA",
    "lt-LT",
    "lv-LV",
    "mk-MK",
    "mn-MN",
    "mr-IN",
    "ms-MY",
    "my-MM",
    "ne-IN",
    "ne-NP",
    "nl-NL",
    "no-NO",
    "om-ET",
    "pa-IN",
    "pa-PK",
    "pl-PL",
    "pt-BR",
    "pt-PT",
    "ro-RO",
    "ru-RU",
    "si-LK",
    "sk-SK",
    "sl-SI",
    "sq-AL",
    "sr-BA",
    "sr-ME",
    "sr-RS",
    "sv-SE",
    "sw-KE",
    "ta-IN",
    "ta-LK",
    "te-IN",
    "ti-ER",
    "ti-ET",
    "tg-TJ",
    "th-TH",
    "tk-TM",
    "tl-PH",
    "tr-TR",
    "uk-UA",
    "ur-PK",
    "uz-UZ",
    "vi-VN",
    "zh-CN",
    "zh-HK",
    "zh-TW",
]
# Only the TWC  5-day forecast API handles the translation of phrases for values of the following data.
# However, when formatting a request URL a valid language must be passed along.
# dayOfWeek,daypartName,moonPhase,qualifierPhrase,uvDescription,windDirectionCardinal,windPhrase,wxPhraseLong

ICON_CONDITION_MAP: Final[dict[str, list[int]]] = {
    ATTR_CONDITION_CLEAR_NIGHT: [31, 33],
    ATTR_CONDITION_CLOUDY: [26, 27, 28],
    ATTR_CONDITION_EXCEPTIONAL: [0, 1, 2, 19, 22, 36],  # 44 is Not Available (N/A)
    ATTR_CONDITION_FOG: [20, 21],
    ATTR_CONDITION_HAIL: [17],
    ATTR_CONDITION_LIGHTNING: [],
    ATTR_CONDITION_LIGHTNING_RAINY: [3, 4, 37, 38, 47],
    ATTR_CONDITION_PARTLYCLOUDY: [29, 30],
    ATTR_CONDITION_POURING: [40],
    ATTR_CONDITION_RAINY: [9, 11, 12, 39, 45],
    ATTR_CONDITION_SNOWY: [13, 14, 15, 16, 41, 42, 43, 46],
    ATTR_CONDITION_SNOWY_RAINY: [5, 6, 7, 8, 10, 18, 25, 35],
    ATTR_CONDITION_SUNNY: [32, 34],
    ATTR_CONDITION_WINDY: [23, 24],
    ATTR_CONDITION_WINDY_VARIANT: [],
}


FIELD_CLOUD_COVER = "cloudCover"
FIELD_DAYPART = "daypart"
FIELD_DESCRIPTION = "wxPhraseLong"
FIELD_HUMIDITY = "relativeHumidity"
FIELD_PRECIPCHANCE = "precipChance"
FIELD_PRESSURE = "pressureAltimeter"
FIELD_QPF = "qpf"
FIELD_TEMPERATUREMAX = "temperatureMax"
FIELD_TEMPERATUREMIN = "temperatureMin"
FIELD_TEMP = "temperature"
FIELD_VALIDTIMEUTC = "validTimeUtc"
FIELD_WINDDIR = "windDirection"
FIELD_WINDGUST = "windGust"
FIELD_WINDSPEED = "windSpeed"
FIELD_CONDITIONS = "condition"


SENSOR_MAP: Final[dict[str, str]] = {
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
    "validTimeLocal": "layout.primary.slots.left-major.modules.0.asAt",
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
}

CONDITION_MAP: Final[dict[str, str]] = {
    # Every newly detected entry should be added to this list, mapping to homeassistant's supported values from below.
    # These initial entries are as found on https://about.metservice.com/our-company/learning-centre/weather-icons-explained/
    "fine": "sunny",
    "partly-cloudy": "partlycloudy",
    "cloudy": "cloudy",
    "mostly-cloudy": "cloudy",
    "showers": "rainy",
    "few-showers": "rainy",
    "drizzle": "rainy",
    "rain": "rainy",
    "fog": "fog",
    "snow": "snowy",
    "wind": "windy",
    "wind-rain": "rainy",
    "thunder": "lightning",
    "hail": "hail",
    "frost": "clear-night",
    # supported values below:
    # "clear-night": "clear-night",
    # "cloudy": "cloudy",
    # "exceptional": "exceptional",
    # "fog": "fog",
    # "hail": "hail",
    # "lightning": "lightning",
    # "lightning-rainy": "lightning-rainy",
    # "partlycloudy": "partlycloudy",
    # "pouring": "pouring",
    # "rainy": "rainy",
    # "snowy": "snowy",
    # "snowy-rainy": "snowy-rainy",
    # "sunny": "sunny",
    # "windy": "windy",
    # "windy-variant": "windy-variant",
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


DEFAULT_LANG = "en-US"
API_URL = "https://www.metservice.com/publicData/webdata/towns-cities"
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
ICON_UMBRELLA = "mdi:umbrella"
ICON_WIND = "mdi:weather-windy"
