#!/usr/bin/env python
"""Example showing how to bulk view hosts using the Censys Platform API."""

import json
import os
import sys

from censys.common.config import get_config
from censys.platform import CensysHosts

# Load configuration
config = get_config()

# Get token from environment or config
CENSYS_PLATFORM_TOKEN = os.environ.get("CENSYS_PLATFORM_TOKEN") or config.get(
    "DEFAULT", "platform_token"
)

# Get organization ID from environment or config (required)
CENSYS_ORGANIZATION_ID = os.environ.get("CENSYS_ORGANIZATION_ID") or config.get(
    "DEFAULT", "platform_org_id"
)

if not CENSYS_PLATFORM_TOKEN:
    print("Error: Censys Platform Token is required")
    print(
        "Set the CENSYS_PLATFORM_TOKEN environment variable or configure it using 'censys platform config'"
    )
    sys.exit(1)

if not CENSYS_ORGANIZATION_ID:
    print("Error: Censys Organization ID is required")
    print(
        "Set the CENSYS_ORGANIZATION_ID environment variable or configure it using 'censys platform config'"
    )
    sys.exit(1)

# Initialize the Hosts API client with required organization ID
hosts = CensysHosts(token=CENSYS_PLATFORM_TOKEN, organization_id=CENSYS_ORGANIZATION_ID)

# Define a list of IP addresses to look up
ip_addresses = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]

# Retrieve host details for multiple IP addresses at once
host_details = hosts.bulk_view(ip_addresses)

# Print the results
print(f"Host details for {len(ip_addresses)} IPs:")
print(json.dumps(host_details, indent=2))

# You can also access individual hosts from the results
if "result" in host_details:
    print("\nIndividual host summaries:")
    for host_result in host_details["result"]:
        if "host" in host_result and "ip" in host_result["host"]:
            ip = host_result["host"]["ip"]
            print(f"- {ip}: {len(host_result)} fields returned")
