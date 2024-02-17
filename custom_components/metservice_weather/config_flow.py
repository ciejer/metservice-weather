"""Config Flow to configure MetService NZ Integration."""
from __future__ import annotations
import logging
from http import HTTPStatus
import async_timeout
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_LOCATION, CONF_NAME, CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
)


from .const import (
    DOMAIN,
    DEFAULT_LOCATION,
    LOCATIONS,
)
# Add constantS for the tide step
CONF_REGION = "tide_region"
CONF_TIDE_REGION_URL = "tide_region_url"
CONF_TIDE_URL = "tide_url"
CONF_ENABLE_TIDES = "enable_tides"

_LOGGER = logging.getLogger(__name__)

CONF_API = "api"

class WeatherFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a MetService config flow."""

    VERSION = 1
    async def async_step_user(self, user_input=None):
        """Allow user to decide between mobile API or public API."""
        if user_input is None:
            return await self._show_user_form(user_input)

        self.user_info = user_input
        self.user_info[CONF_ENABLE_TIDES] = user_input.get(CONF_ENABLE_TIDES, True)

        if user_input["api"] == "mobile":
            return await self.async_step_mobile()
        else:
            return await self.async_step_public()

    async def _show_user_form(self, errors=None):
        """Show the init form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_API, default="public"
                    ): SelectSelector(SelectSelectorConfig(options=["public", "mobile"])),
                    vol.Optional(CONF_ENABLE_TIDES, default=True): bool,
                }
            ),
            errors=errors or {},
        )


    async def async_step_public(self, user_input=None):
        """Handle a flow initiated by the user."""
        if user_input is None:
            return await self._show_public_form(user_input)

        errors = {}
        session = async_create_clientsession(self.hass)

        location = user_input[CONF_LOCATION]
        location_name = user_input[CONF_NAME]
        headers = {
            "Accept-Encoding": "gzip",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        }
        try:
            with async_timeout.timeout(10):
                # Use English and US units for the initial test API call. User-supplied units and language will be used for
                # the created entities.
                url = f"https://www.metservice.com/publicData/webdata{location}"
                response = await session.get(url, headers=headers)
            # _LOGGER.debug(response.status)
            if response.status != HTTPStatus.OK:
                # 401 status is most likely bad api_key or api usage limit exceeded

                _LOGGER.error(
                    "MetService config responded with HTTP error %s: %s",
                    response.status,
                    response.reason,
                )
                raise Exception
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown_error"
            return await self._show_public_form(errors=errors)

        if not errors:
            await response.json(content_type=None)

            unique_id = str(f"{DOMAIN}-{location}")
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            self.user_info[CONF_LOCATION] = user_input[CONF_LOCATION]
            self.user_info[CONF_NAME] = location_name
            self.user_info[CONF_API] = "public"
            if not self.user_info.get(CONF_ENABLE_TIDES, True):
                # The user has opted out of tides functionality, skip to creating entry
                return self.async_create_entry(
                    title=self.user_info[CONF_NAME],
                    data=self.user_info,
                )
            return await self.async_step_tide_region()

    async def _show_public_form(self, errors=None):
        """Show the setup form to the user."""

        return self.async_show_form(
            step_id="public",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_LOCATION, default=DEFAULT_LOCATION
                    ): SelectSelector(SelectSelectorConfig(options=LOCATIONS)),
                    vol.Required(
                        CONF_NAME, default=self.hass.config.location_name
                    ): str,
                }
            ),
            errors=errors or {},
        )

    async def async_step_mobile(self, user_input=None):
        """Handle a flow initiated by the user."""
        if user_input is None:
            return await self._show_mobile_form(user_input)

        errors = {}
        session = async_create_clientsession(self.hass)

        api_key = user_input[CONF_API_KEY]
        location_name = user_input[CONF_NAME]
        headers = {
            "Accept": "*/*",
            "User-Agent": "MetServiceNZ/2.19.3 (com.metservice.iphoneapp; build:332; iOS 17.1.1) Alamofire/5.4.3",
            "Accept-Language": "en-CA;q=1.0",
            "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
            "Connection": "keep-alive",
            "apiKey": api_key
        }
        try:
            with async_timeout.timeout(10):
                # Use English and US units for the initial test API call. User-supplied units and language will be used for
                # the created entities.
                url = "https://api.metservice.com/mobile/nz/weatherData/-43.123/172.123"
                response = await session.get(url, headers=headers)
            # _LOGGER.debug(response.status)
            if response.status != HTTPStatus.OK:
                # 401 status is most likely bad api_key or api usage limit exceeded

                _LOGGER.error(
                    "MetService config responded with HTTP error %s: %s",
                    response.status,
                    response.reason,
                )
                raise Exception
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown_error"
            return await self._show_mobile_form(errors=errors)

        if not errors:
            await response.json(content_type=None)

            unique_id = str(f"{DOMAIN}-{location_name}")
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            self.user_info[CONF_API_KEY] = api_key
            self.user_info[CONF_NAME] = location_name
            self.user_info[CONF_API] = "mobile"
            if not self.user_info.get(CONF_ENABLE_TIDES, True):
                # The user has opted out of tides functionality, skip to creating entry
                return self.async_create_entry(
                    title=self.user_info[CONF_NAME],
                    data=self.user_info,
                )
            return await self.async_step_tide_region()

    async def _show_mobile_form(self, errors=None):
        """Show the setup form to the user."""
        return self.async_show_form(
            step_id="mobile",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_API_KEY, default=""
                    ): str,
                    vol.Required(
                        CONF_NAME, default=self.hass.config.location_name
                    ): str,
                }
            ),
            errors=errors or {},
        )
    @callback
    def _async_generate_select_schema_region(self, options: list[dict], field_name: str) -> vol.Schema:
        """Generate a schema with a dynamic SelectSelector based on options provided."""
        select_options = {opt['heading']['label']: opt['heading']['url'] for opt in options}
        return vol.Schema(
            {
                vol.Required(field_name): SelectSelector(SelectSelectorConfig(options=list(select_options.keys()))),
            }
        )
    @callback
    def _async_generate_select_schema_location(self, options: list[dict], field_name: str) -> vol.Schema:
        """Generate a schema with a dynamic SelectSelector based on options provided."""
        self.locations_map = {str(index): opt['label'] for index, opt in enumerate(options)}
        return vol.Schema(
            {
                vol.Required(field_name): SelectSelector(SelectSelectorConfig(options=list(self.locations_map.values()))),
            }
        )
    def get_tide_location_url_from_label(self, label):
        """Get the URL for the selected tide location."""
        for index, location_label in self.locations_map.items():
            if location_label == label:
                # Assuming `self.locations` is the original list of dicts from which `locations_map` was made:
                return self.locations[int(index)]['action']
        return None

    async def async_step_tide_region(self, user_input=None):
        """Handle selecting a tide region."""
        if user_input is None:
            # Make the REST call to get the list of regions
            session = async_create_clientsession(self.hass)
            response = await session.get('https://www.metservice.com/publicData/webdata/marine')
            regions_data = await response.json()
            self.regions = regions_data['layout']['search']['searchLocations'][0]['items']

            return self.async_show_form(
                step_id="tide_region",
                data_schema=self._async_generate_select_schema_region(self.regions, CONF_REGION),
            )
        # Save the selected region's URL and move to the next step
        selected_label = user_input[CONF_REGION]
        selected_region = next((item for item in self.regions if item['heading']['label'] == selected_label), None)
        self.user_info[CONF_TIDE_REGION_URL] = selected_region['heading']['url'] if selected_region else None
        return await self.async_step_tide_location()

    async def async_step_tide_location(self, user_input=None):
        """Handle selecting a specific tide location within the region."""
        if user_input is None:
            region = self.user_info[CONF_TIDE_REGION_URL]
            # Make the REST call for the locations within the selected region
            url = f"https://www.metservice.com/publicData/webdata/{region}/tides"
            session = async_create_clientsession(self.hass)
            response = await session.get(url)
            locations_data = await response.json()
            self.locations = locations_data['layout']['primary']['map']['modules'][0]['markers']  # Adjust this based on the actual structure of the response
            return self.async_show_form(
                step_id="tide_location",
                data_schema=self._async_generate_select_schema_location(self.locations, CONF_TIDE_URL),
            )
        else:
            # User has selected a location, find the URL and save the data to finish the config flow
            selected_label = user_input[CONF_TIDE_URL]
            tide_url = self.get_tide_location_url_from_label(selected_label)
            if tide_url:
                session = async_create_clientsession(self.hass)
                tide_url = f"https://www.metservice.com/publicData/webdata/{tide_url}"
                self.user_info[CONF_TIDE_URL] = tide_url
                try:
                    with async_timeout.timeout(10):
                        # Use English and US units for the initial test API call. User-supplied units and language will be used for
                        # the created entities.
                        headers = {
                            "Accept-Encoding": "gzip",
                            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
                        }
                        response = await session.get(tide_url, headers=headers)
                    # _LOGGER.debug(response.status)
                    if response.status != HTTPStatus.OK:
                        # 401 status is most likely bad api_key or api usage limit exceeded

                        _LOGGER.error(
                            "MetService config responded with HTTP error %s: %s",
                            response.status,
                            response.reason,
                        )
                        raise Exception
                except Exception:  # pylint: disable=broad-except
                    _LOGGER.exception("Unexpected exception")
                    return self.async_show_form(
                        step_id="tide_location",
                        data_schema=self._async_generate_select_schema_location(self.locations, CONF_TIDE_URL),
                    )

            else:
                # Handle error case where URL is not found
                return self.async_show_form(
                    step_id="tide_location",
                    data_schema=self._async_generate_select_schema_location(self.locations, CONF_TIDE_URL),
                )

        # Now you can create the entry with all the necessary information
        return self.async_create_entry(
            title=self.user_info[CONF_NAME],
            data=self.user_info,
        )
