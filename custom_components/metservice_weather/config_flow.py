"""Config Flow to configure MetService NZ Integration."""
from __future__ import annotations
import logging
from http import HTTPStatus
import async_timeout
import voluptuous as vol
from homeassistant import config_entries
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
                        CONF_API, default="mobile"
                    ): SelectSelector(SelectSelectorConfig(options=["mobile", "public"])),
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

            return self.async_create_entry(
                title=location_name,
                data={
                    CONF_LOCATION: user_input[CONF_LOCATION],
                    CONF_NAME: location_name,
                    CONF_API: "public",
                },
            )

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

            return self.async_create_entry(
                title=location_name,
                data={
                    CONF_API_KEY: api_key,
                    CONF_NAME: location_name,
                    CONF_API: "mobile",
                },
            )

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
