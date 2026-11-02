"""Sensors for AdGuard Home DHCP clients."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import parse_leases
from .const import CONF_INCLUDE_IPV6, DEFAULT_INCLUDE_IPV6, DOMAIN
from .coordinator import AdGuardDHCPCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the DHCP clients sensor."""
    coordinator: AdGuardDHCPCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AdGuardDHCPLeaseCountSensor(coordinator, entry)])


class AdGuardDHCPLeaseCountSensor(CoordinatorEntity[AdGuardDHCPCoordinator], SensorEntity):
    """Expose the current DHCP lease count and normalized lease list."""

    _attr_has_entity_name = True
    _attr_name = "DHCP clients"
    _attr_icon = "mdi:lan-connect"

    def __init__(self, coordinator: AdGuardDHCPCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_dhcp_clients"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"AdGuard Home ({entry.data['host']})",
            manufacturer="AdGuard",
            model="AdGuard Home",
            configuration_url=coordinator.base_url,
        )

    @property
    def native_value(self) -> int:
        """Return the number of usable DHCP lease records."""
        return len(self._leases)

    @property
    def extra_state_attributes(self) -> dict[str, list[dict[str, str]]]:
        """Return each lease's hostname, IP address, and MAC address when present."""
        return {"leases": self._leases}

    @property
    def _leases(self) -> list[dict[str, str]]:
        """Return leases using this entry's IPv6 preference."""
        entry = self.coordinator.entry
        include_ipv6 = entry.options.get(
            CONF_INCLUDE_IPV6,
            entry.data.get(CONF_INCLUDE_IPV6, DEFAULT_INCLUDE_IPV6),
        )
        return parse_leases(self.coordinator.data, include_ipv6=include_ipv6)
