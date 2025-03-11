#!/usr/bin/env python
"""Example showing how to view certificate details using the Censys Platform API."""

import json
import os
import sys

from censys.common.config import get_config
from censys.platform import CensysCertificates

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

# Initialize the Certificates API client with required organization ID
certificates = CensysCertificates(
    token=CENSYS_PLATFORM_TOKEN, organization_id=CENSYS_ORGANIZATION_ID
)

# Specify the certificate hash to lookup
# Replace this with a valid certificate hash
cert_hash = "fb444eb8e68437bae06232b9f5091bccff62a768ca09e92eb5c9c2cf9d17c426"

# Retrieve certificate details
cert_details = certificates.view(cert_hash)

# Print the result with nice formatting
print(f"Certificate Details for {cert_hash}:")
print(json.dumps(cert_details, indent=2))
