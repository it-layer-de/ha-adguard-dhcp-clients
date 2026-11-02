"""AdGuard Home control API helpers."""
from __future__ import annotations
from homeassistant.util import dt as dt_util
from collections.abc import Mapping
import ipaddress
from typing import Any

import aiohttp

ENDPOINT = "/control/dhcp/status"


class AdGuardDHCPApiError(Exception):
    """Raised when the AdGuard DHCP status API returns an invalid response."""


def make_base_url(host: str, port: int, use_https: bool) -> str:
    """Build the AdGuard Home base URL from user configuration."""
    scheme = "https" if use_https else "http"
    return f"{scheme}://{host.strip().rstrip('/')}:{port}"


async def async_fetch_status(
    session: aiohttp.ClientSession, base_url: str, username: str, password: str
) -> dict[str, Any]:
    """Fetch and validate the DHCP status response."""
    try:
        async with session.get(
            f"{base_url}{ENDPOINT}",
            auth=aiohttp.BasicAuth(username, password),
            timeout=aiohttp.ClientTimeout(total=15),
        ) as response:
            response.raise_for_status()
            payload = await response.json(content_type=None)
    except (aiohttp.ClientError, TimeoutError, ValueError) as err:
        raise AdGuardDHCPApiError(f"Unable to fetch DHCP status: {err}") from err

    if not isinstance(payload, Mapping):
        raise AdGuardDHCPApiError("DHCP status response must be a JSON object")
    leases = payload.get("leases", [])
    if not isinstance(leases, list):
        raise AdGuardDHCPApiError("DHCP status 'leases' field must be a list")
    return dict(payload)


def parse_leases(
    payload: Mapping[str, Any], include_ipv6: bool = True
) -> list[dict[str, str]]:
    """Combine dynamic and static DHCP leases, optionally excluding IPv6."""
    normalized: list[dict[str, str]] = []
    seen: set[str] = set()

    for source in ("leases", "static_leases"):
        leases = payload.get(source, [])
        if not isinstance(leases, list):
            continue

        for lease in leases:
            if not isinstance(lease, Mapping):
                continue

            item: dict[str, str | int] = {}
            for key in ("hostname", "ip", "mac"):
                value = lease.get(key)
                if isinstance(value, (str, int, float)) and str(value).strip():
                    item[key] = str(value).strip()

            if not item.get("ip") and not item.get("mac"):
                continue

            if source == "static_leases":
                item["expires"] = "Statischer Eintrag"
            else:
                expires = lease.get("expires")
                parsed = dt_util.parse_datetime(str(expires)) if expires else None
                if parsed is not None:
                    local_expires = dt_util.as_local(parsed)
                    item["expires"] = local_expires.strftime("%Y.%m.%d %H:%M:%S")
                    item["expires_sort"] = int(local_expires.timestamp())
                else:
                    item["expires"] = "Statischer Eintrag"

            if not include_ipv6 and item.get("ip"):
                try:
                    is_ipv6 = ipaddress.ip_address(str(item["ip"])).version == 6
                except ValueError:
                    is_ipv6 = False
                if is_ipv6:
                    continue

            identity = (
                f"mac:{str(item['mac']).lower()}"
                if item.get("mac")
                else f"ip:{item['ip']}"
            )
            if identity in seen:
                continue

            seen.add(identity)
            normalized.append(item)

    return normalized
