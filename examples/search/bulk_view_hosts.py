"""Bulk IP Lookup Example."""
from censys.search import CensysHosts

h = CensysHosts()

IPS = [
    "1.1.1.1",
    "1.1.1.2",
    "1.1.1.3",
]

hosts = h.bulk_view(IPS)
# {
#     "1.1.1.1": {...},
#     "1.1.1.2": {...},
#     "1.1.1.3": {...},
# }
