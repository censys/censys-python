#!/usr/bin/env python
"""Example showing how to retrieve a host's timeline using the Censys Platform API."""

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

# Define the timeframe
end_time = datetime.utcnow()
start_time = end_time - timedelta(days=30)  # Last 30 days

# Retrieve the host's timeline
print(f"Retrieving timeline for {ip_address} from {start_time} to {end_time}")
timeline = hosts.get_host_timeline(ip_address, start_time=start_time, end_time=end_time)

# Print the results
print(f"Timeline events for {ip_address}:")
print(json.dumps(timeline, indent=2))
