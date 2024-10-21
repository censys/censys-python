"""Aggregate hosts data set."""

from censys.search import SearchClient

c = SearchClient()

# The aggregate method constructs a report using a query, an aggregation field, and the
# number of buckets to bin.
report = c.v2.hosts.aggregate(
    "services.service_name: HTTP",
    "services.port",
    num_buckets=5,
)
print(report)
# {
#     "total": 987342156,
#     "total_omitted": 836949090,
#     "potential_deviation": 3965103,
#     "buckets": [
#         {"key": "80", "count": 58727150},
#         {"key": "443", "count": 46716751},
#         {"key": "7547", "count": 19185117},
#         {"key": "22", "count": 13276559},
#         {"key": "30005", "count": 12487489},
#     ],
#     "query": "services.service_name: HTTP",
#     "field": "services.port",
# }

# You can also specify whether to include virtual hosts in the report.
report = c.v2.hosts.aggregate(
    "services.service_name: HTTP",
    "services.port",
    num_buckets=5,
    virtual_hosts="INCLUDE",
)
print(report)
