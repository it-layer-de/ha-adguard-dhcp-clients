# AdGuard Home DHCP Clients

A Home Assistant custom integration that reports current DHCP leases from AdGuard Home as a sensor. It reads the AdGuard Home control API endpoint `/control/dhcp/status` using HTTP Basic Authentication.

## Features

- Sensor state: number of usable DHCP lease records returned in the API `leases` array.
- `leases` attribute: a list of records containing available `hostname`, `ip`, and `mac` fields.
- Polls AdGuard Home every 60 seconds.
- Supports HTTP or HTTPS and a configurable port.

## Installation with HACS

1. In HACS, open **Integrations** and select **Custom repositories** from the menu.
2. Add `https://github.com/it-layer-de/ha-adguard-dhcp-clients` with category **Integration**.
3. Install **AdGuard Home DHCP Clients** and restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration**, then search for **AdGuard Home DHCP Clients**.

## Configuration

Enter the AdGuard Home hostname or IP address, API port (usually `3000`), username, and password. Enable HTTPS only if the AdGuard Home control interface is configured for HTTPS. The host field should not include a scheme, path, or port; enter the port separately.

The configured account must be able to authenticate to the AdGuard Home control API. The integration validates the connection during setup and reads `/control/dhcp/status` with Basic Auth.

## Sensor attributes

The sensor entity is named **DHCP clients**. Its state is the count of valid lease entries. The `leases` attribute contains normalized lease objects. Entries without both IP and MAC are retained when at least one of those identifiers is available; malformed entries and entries without either identifier are ignored. Missing hostnames or identifiers are omitted from each object.

This integration reports the current dynamic `leases` list from AdGuard's DHCP status response. It does not count the separate `static_leases` configuration list as active leases.

## Display DHCP clients in Lovelace

To display the DHCP clients in a searchable table, install **Flex Table Card** separately. It is available through HACS as a Lovelace card; it is not included with this integration.

Add a **Manual card** to your dashboard and use the following YAML:

```yaml
type: custom:flex-table-card
title: AdGuard DHCP Clients
entities:
  include:
    - sensor.adguard_dhcp_clientliste
columns:
  - name: Hostname
    data: leases.hostname
  - name: IP
    data: leases.ip
  - name: MAC
    data: leases.mac
enable_search: true
sort_by: +IP
```

Replace `sensor.adguard_dhcp_clientliste` with the entity ID of your DHCP clients sensor if it is different. You can find the entity ID under **Settings → Devices & services → Entities**.

## Troubleshooting

- Check that the host and port are reachable from Home Assistant.
- Confirm Basic Auth credentials and whether the control API uses HTTPS.
- Inspect Home Assistant logs for API connection or response errors.

## Project

Source and issue tracking: https://github.com/it-layer-de/ha-adguard-dhcp-clients