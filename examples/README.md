# Examples

Examples for using the Python Library.

## Imports

For our package import statements are structured like this.

### Search

```python
# Access all indexes
from censys.search import SearchClient

# Access only the hosts index
from censys.search import CensysHosts

# Access only the certificates index
from censys.search import CensysCertificates
```

### ASM

```python
from censys.asm import AsmClient
```

## Available Examples

### Search Examples

- [Using `SearchClient`](search/search_client.py)

#### Hosts Index

- [View Host](search/view_host.py)
- [Search Hosts](search/search_hosts.py)
- [Aggregate Hosts](search/aggregate_hosts.py)
- [Bulk View Hosts](search/bulk_view_hosts.py)
- [Hosts Metadata](search/metadata_hosts.py)
- [View Host Events](search/view_host_events.py)
- [View Host Names](search/view_host_names.py)
- [View Host Diff](search/view_host_diff.py)

#### Certificates Index

- [View Certificate](search/view_cert.py)
- [Search Certificates](search/search_certs.py)
- [Report Certificates](search/report_certs.py)

### ASM Examples

- [Get Cloud Host Counts](asm/cloud_host_count.py)
- [Get Host Ricks](asm/get_host_risks.py)
- [Get Domains and Subdomains](asm/get_subdomains.py)
- [Add Seeds in Bulk (from CSV)](asm/add_seeds_bulk.py)
