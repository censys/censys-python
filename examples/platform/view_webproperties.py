#!/usr/bin/env python
"""Example showing how to view web properties using the Censys Platform API."""

import json
import os
import sys
from datetime import datetime, timedelta

from censys.common.config import get_config
from censys.platform import CensysWebProperties

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

# Initialize the WebProperties API client with required organization ID
webproperties = CensysWebProperties(
    token=CENSYS_PLATFORM_TOKEN, organization_id=CENSYS_ORGANIZATION_ID
)

# Specify the WebProperty ID to lookup
webproperty_id = "google.com:443"

# Retrieve webproperty details
webproperty_details = webproperties.view(webproperty_id)

# Print the result with nice formatting
print(f"WebProperty Details for {webproperty_id}:")
print(json.dumps(webproperty_details, indent=2))

# Example: Get webproperty details at a specific time (1 week ago)
one_week_ago = datetime.utcnow() - timedelta(days=7)
print(f"\nWebProperty Details for {webproperty_id} from one week ago:")
historical_details = webproperties.view(webproperty_id, at_time=one_week_ago)
print(json.dumps(historical_details, indent=2))

# Example: Bulk view multiple web properties
multi_props = ["example.com:443", "example.org:443", "example.net:443"]
print(f"\nBulk viewing {len(multi_props)} web properties:")
bulk_results = webproperties.bulk_view(multi_props)
print(json.dumps(bulk_results, indent=2))
