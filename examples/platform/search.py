#!/usr/bin/env python
"""Example showing how to use search with the Censys Platform API."""

import json
import os
import sys
import traceback

from censys.common.config import get_config
from censys.common.exceptions import CensysAPIException
from censys.platform import CensysSearch

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

# Initialize the Search API client with required organization ID
search = CensysSearch(
    token=CENSYS_PLATFORM_TOKEN, organization_id=CENSYS_ORGANIZATION_ID
)

try:
    # Example 1: Simple Search Query
    print("Example 1: Simple Search Query")
    # Using a very simple query with a different format
    simple_query = 'host.ip: "8.8.8.8"'
    print(f"Query: {simple_query}")

    simple_results = search.query(simple_query, page_size=10)

    # Print total and sample results
    print(f"Found {simple_results.get('result', {}).get('total', 0)} results")
    print("Sample hosts:")
    for host in simple_results.get("result", {}).get("hits", []):
        print(f"  - {host.get('ip')} ({host.get('name', 'No name')})")

    # Example 2: Advanced Search Query with multiple filters
    print("\nExample 2: Advanced Search Query")
    # Using a simpler advanced query with a different format
    advanced_query = 'web.endpoints.http.html_title: "Google"'
    print(f"Query: {advanced_query}")
    advanced_results = search.query(advanced_query, page_size=5)

    # Print the JSON results with formatting
    print(f"Found {advanced_results.get('result', {}).get('total', 0)} results")
    print("First result:")
    if advanced_results.get("result", {}).get("hits", []):
        print(
            json.dumps(advanced_results.get("result", {}).get("hits", [])[0], indent=2)
        )
    else:
        print("No results found")

except CensysAPIException as e:
    print(f"API Exception: {e}")
    print(f"Status code: {getattr(e, 'status_code', 'unknown')}")
    print(f"Error code: {getattr(e, 'error_code', 'unknown')}")
    print(f"Error message: {getattr(e, 'message', 'unknown')}")
    print(f"Details: {getattr(e, 'details', 'unknown')}")
    traceback.print_exc()
except Exception as e:
    print(f"Unexpected error: {e}")
    traceback.print_exc()
