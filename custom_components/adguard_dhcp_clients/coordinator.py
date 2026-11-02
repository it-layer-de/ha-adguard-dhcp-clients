"""Coordinator for AdGuard Home DHCP status polling."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AdGuardDHCPApiError, async_fetch_status, make_base_url
from .const import CONF_USE_HTTPS, UPDATE_INTERVAL


class AdGuardDHCPCoordinator(DataUpdateCoordinator[dict]):
    """Fetch DHCP lease data from AdGuard Home on a regular interval."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name="AdGuard Home DHCP clients",
            update_interval=UPDATE_INTERVAL,
        )
        self.entry = entry
        self.base_url = make_base_url(
            entry.data["host"], entry.data["port"], entry.data[CONF_USE_HTTPS]
        )

    async def _async_update_data(self) -> dict:
        """Retrieve a fresh DHCP status snapshot."""
        try:
            return await async_fetch_status(
                async_get_clientsession(self.hass),
                self.base_url,
                self.entry.data["username"],
                self.entry.data["password"],
            )
        except AdGuardDHCPApiError as err:
            raise UpdateFailed(str(err)) from err
