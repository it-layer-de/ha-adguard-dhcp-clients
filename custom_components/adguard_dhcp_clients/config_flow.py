"""Config flow for AdGuard Home DHCP clients."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AdGuardDHCPApiError, async_fetch_status, make_base_url
from .const import CONF_USE_HTTPS, DOMAIN


def _schema(user_input: dict | None = None) -> vol.Schema:
    """Return the configuration form schema."""
    values = user_input or {}
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=values.get(CONF_HOST, "")): str,
            vol.Required(CONF_PORT, default=values.get(CONF_PORT, 3000)): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=65535)
            ),
            vol.Required(CONF_USERNAME, default=values.get(CONF_USERNAME, "")): str,
            vol.Required(CONF_PASSWORD, default=values.get(CONF_PASSWORD, "")): str,
            vol.Optional(CONF_USE_HTTPS, default=values.get(CONF_USE_HTTPS, False)): bool,
        }
    )


async def _validate_input(hass: HomeAssistant, data: dict) -> None:
    """Verify credentials and API availability."""
    base_url = make_base_url(data[CONF_HOST], data[CONF_PORT], data[CONF_USE_HTTPS])
    await async_fetch_status(
        async_get_clientsession(hass), base_url, data[CONF_USERNAME], data[CONF_PASSWORD]
    )


class AdGuardDHCPConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AdGuard Home DHCP clients."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Handle the initial setup step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            user_input[CONF_HOST] = user_input[CONF_HOST].strip().rstrip("/")
            if not user_input[CONF_HOST] or "://" in user_input[CONF_HOST] or "/" in user_input[CONF_HOST]:
                errors["base"] = "invalid_host"
            else:
                await self.async_set_unique_id(
                    f"{user_input[CONF_HOST].lower()}:{user_input[CONF_PORT]}:{user_input[CONF_USE_HTTPS]}"
                )
                self._abort_if_unique_id_configured()
                try:
                    await _validate_input(self.hass, user_input)
                except AdGuardDHCPApiError:
                    errors["base"] = "cannot_connect"
                except Exception:
                    errors["base"] = "unknown"
                else:
                    return self.async_create_entry(
                        title=f"AdGuard Home ({user_input[CONF_HOST]})", data=user_input
                    )
        return self.async_show_form(
            step_id="user", data_schema=_schema(user_input), errors=errors
        )
