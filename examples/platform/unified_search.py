#!/usr/bin/env python
"""Example showing how to use the unified Censys Query Language (CenQL) with the Censys Platform API."""

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
# This provides access to all APIs through a single client
client = CensysPlatformClient(
    token=CENSYS_PLATFORM_TOKEN, organization_id=CENSYS_ORGANIZATION_ID
)

print("Censys Query Language (CenQL) Examples")
print("=====================================")

# ---------------------------------------------
# Example 1: Simple field queries
# ---------------------------------------------
print("\n1. Simple Field Queries")
print("----------------------")

# Hosts query with field operators
hosts_query = "host.services.port: 443 AND host.services.service_name: HTTPS"
print(f"Hosts query: {hosts_query}")
hosts_results = client.search.query(hosts_query, per_page=2)
print(f"Found {hosts_results.get('result', {}).get('total', 0)} matching hosts")
if hosts_results.get("result", {}).get("hits"):
    print("Sample host IP:", hosts_results["result"]["hits"][0].get("ip"))

# Web properties query with equality operator
webprops_query = "webproperty.protocol = HTTPS AND webproperty.services.http.response.html_title: Google"
print(f"\nWeb properties query: {webprops_query}")
webprops_results = client.search.query(webprops_query, page_size=2)
print(
    f"Found {webprops_results.get('result', {}).get('total', 0)} matching web properties"
)
if webprops_results.get("result", {}).get("hits"):
    print("Sample web property:", webprops_results["result"]["hits"][0].get("name"))

# Certificates query with wildcard
cert_query = "certificate.issuer.common_name: *Google*"
print(f"\nCertificates query: {cert_query}")
cert_results = client.search.query(cert_query, page_size=2)
print(f"Found {cert_results.get('result', {}).get('total', 0)} matching certificates")
if cert_results.get("result", {}).get("hits"):
    print(
        "Sample certificate fingerprint:",
        cert_results["result"]["hits"][0].get("fingerprint"),
    )

# ---------------------------------------------
# Example 2: Advanced field queries
# ---------------------------------------------
print("\n2. Advanced Field Queries")
print("------------------------")

# Advanced query with comparison operators
advanced_query = "host.services.port: 22 AND host.services.service_name: SSH"
print(f"Query: {advanced_query}")
advanced_results = client.search.query(advanced_query, per_page=2)
print(f"Found {advanced_results.get('result', {}).get('total', 0)} matching hosts")

# Advanced query with NOT operator
not_query = "host.services.port: 443 AND NOT host.services.service_name: HTTPS"
print(f"\nNOT query: {not_query}")
not_results = client.search.query(not_query, page_size=2)
print(f"Found {not_results.get('result', {}).get('total', 0)} matching hosts")

# ---------------------------------------------
# Example 3: Nested field queries
# ---------------------------------------------
print("\n3. Nested Field Queries")
print("----------------------")

# Nested field query for specific service and port
nested_query = 'host.services.banner: "Apache"'
print(f"Query: {nested_query}")
nested_results = client.search.query(nested_query, per_page=2)
print(f"Found {nested_results.get('result', {}).get('total', 0)} matching hosts")

# 4. Complex Nested Field Queries
print("\n4. Complex Nested Field Queries")
print("------------------------------")

complex_nested_query = 'host.services.banner: "Apache" AND host.services.port: 80'
print(f"Query: {complex_nested_query}")
complex_results = client.search.query(complex_nested_query, per_page=2)
print(f"Found {complex_results.get('result', {}).get('total', 0)} matching hosts")

# ---------------------------------------------
# Example 5: Specialized search techniques
# ---------------------------------------------
print("\n5. Specialized Search Techniques")
print("------------------------------")

# Regex matching
regex_query = "host.names =~ '.*\\.google\\.com'"
print(f"\nRegex query: {regex_query}")
regex_results = client.search.query(regex_query, per_page=2)
print(f"Found {regex_results.get('result', {}).get('total', 0)} matching hosts")

# Non-zero value matching (finding hosts with any value for a field)
exists_query = "host.services.http.response.html_title: *"
print(f"\nExists query: {exists_query}")
exists_results = client.search.query(exists_query, per_page=2)
print(f"Found {exists_results.get('result', {}).get('total', 0)} matching hosts")

# ---------------------------------------------
# Example 6: Aggregations
# ---------------------------------------------
print("\n6. Aggregations")
print("-------------")

# Aggregate hosts by service name
agg_query = "host.services.port: 443"
agg_field = "host.services.service_name"
print(f"\nAggregating '{agg_field}' where '{agg_query}'")
agg_results = client.search.aggregate(agg_query, agg_field)
buckets = agg_results.get("result", {}).get("buckets", [])
print(f"Found {len(buckets)} buckets")
for i, bucket in enumerate(buckets[:5]):  # Show top 5
    print(f"  {i+1}. {bucket.get('key')}: {bucket.get('count')} hosts")

print("\nCenQL provides a unified query syntax across all Censys data types.")
print("Visit https://docs.censys.com/docs/censys-query-language for more details.")
