"""Constants for metservice_weather."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "MetService New Zealand Weather"
DOMAIN = "metservice_weather"
VERSION = "0.0.0"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
METSERVICE_DISTRICTS = {
    "Tauranga": "tauranga",
    "Hamilton": "hamilton",
}
CONF_DISTRICT = "tauranga"
