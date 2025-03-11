#!/usr/bin/env python
"""Example showing how to use the CensysPlatformClient to access all Censys Platform APIs."""

import os
import sys

from censys.common.config import get_config
from censys.platform import CensysPlatformClient

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

# Initialize the Censys Platform client with required organization ID
client = CensysPlatformClient(
    token=CENSYS_PLATFORM_TOKEN, organization_id=CENSYS_ORGANIZATION_ID
)

print("Censys Platform Client Example")
print("=============================")
print(
    "\nThe CensysPlatformClient provides access to all Censys Platform APIs through a single client:"
)

# Example 1: Search for hosts using the Search API
print("\n1. Search for hosts using the Search API")
print("----------------------------------------")
search_query = "host.services: (port = 443 and protocol = 'TCP')"
print(f"Query: {search_query}")
search_results = client.search.query(search_query, page_size=2)
print(f"Found {search_results.get('result', {}).get('total', 0)} matching hosts")

# Example 2: View a specific host using the Hosts API
print("\n2. View a specific host using the Hosts API")
print("------------------------------------------")
host_ip = "8.8.8.8"
print(f"Viewing host: {host_ip}")
try:
    host_details = client.hosts.view(host_ip)
    print(f"Host Name: {host_details.get('host', {}).get('names', ['Unknown'])[0]}")
    services = host_details.get("host", {}).get("services", [])
    print(f"Services: {len(services)} open ports detected")
    for service in services[:3]:  # Show first 3 services
        print(
            f"  - Port {service.get('port')}: {service.get('service_name', 'Unknown service')}"
        )
except Exception as e:
    print(f"Error viewing host: {e}")

# Example 3: View a certificate using the Certificates API
print("\n3. View a certificate using the Certificates API")
print("-----------------------------------------------")
print("Searching for a Google certificate...")
cert_query = "certificate.issuer.common_name: *Google*"
cert_results = client.search.query(cert_query, page_size=1)
if cert_results.get("result", {}).get("hits"):
    cert_id = cert_results["result"]["hits"][0].get("fingerprint")
    print(f"Found certificate: {cert_id}")
    try:
        cert_details = client.certificates.view(cert_id)
        cert_data = cert_details.get("certificate", {})
        print(f"Subject: {cert_data.get('subject', {}).get('common_name', 'Unknown')}")
        print(f"Issuer: {cert_data.get('issuer', {}).get('common_name', 'Unknown')}")
        print(f"Valid from: {cert_data.get('validity', {}).get('start')}")
        print(f"Valid until: {cert_data.get('validity', {}).get('end')}")
    except Exception as e:
        print(f"Error viewing certificate: {e}")
else:
    print("No matching certificates found")

# Example 4: Aggregate data using the Search API
print("\n4. Aggregate data using the Search API")
print("-------------------------------------")
agg_query = "host.services.port: 443"
agg_field = "host.services.service_name"
print(f"Aggregating {agg_field} where {agg_query}")
try:
    agg_results = client.search.aggregate(agg_query, agg_field)
    buckets = agg_results.get("result", {}).get("buckets", [])
    print("Top service names on port 443:")
    for bucket in buckets[:5]:  # Show top 5
        print(f"  - {bucket.get('key')}: {bucket.get('count')} hosts")
except Exception as e:
    print(f"Error aggregating data: {e}")

print(
    "\nThe CensysPlatformClient provides a unified interface to all Censys Platform APIs."
)
print("You can access the following APIs through this client:")
print("  - client.search: For searching across all data types")
print("  - client.hosts: For host-specific operations")
print("  - client.certificates: For certificate-specific operations")
print("  - client.webproperties: For web property-specific operations")
