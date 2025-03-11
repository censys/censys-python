#!/usr/bin/env python
"""Example showing how to view host details using the Censys Platform API."""

import json
import os
import sys
from datetime import datetime, timedelta

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

# Specify the IP address to lookup
ip_address = "8.8.8.8"

# Retrieve host details
host_details = hosts.view(ip_address)

# Print the result with nice formatting
print(f"Host Details for {ip_address}:")
print(json.dumps(host_details, indent=2))

# Example: Get host details at a specific time (1 week ago)
one_week_ago = datetime.utcnow() - timedelta(days=7)
print(f"\nHost Details for {ip_address} from one week ago:")
historical_details = hosts.view(ip_address, at_time=one_week_ago)
print(json.dumps(historical_details, indent=2))
