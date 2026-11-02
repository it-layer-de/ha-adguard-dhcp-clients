"""Constants for the AdGuard Home DHCP clients integration."""
from datetime import timedelta

DOMAIN = "adguard_dhcp_clients"
CONF_USE_HTTPS = "use_https"
CONF_INCLUDE_IPV6 = "include_ipv6"
DEFAULT_INCLUDE_IPV6 = True
UPDATE_INTERVAL = timedelta(seconds=60)
