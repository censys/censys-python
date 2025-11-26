# Bulk Search Tool for Censys

## Overview
This tool adds bulk-search capability for processing multiple IPs/domains
from a file and exporting results to JSON. Includes `--mock` mode for
development or free-tier accounts without search quota.

## Usage
python3 bulk_search.py -f sample_ips.txt -o results.json --mock

## Example Output
See example_output.json
Save and exit:

Ctrl + O, Enter, Ctrl + X
