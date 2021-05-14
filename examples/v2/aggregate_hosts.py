"""Aggregate hosts data set."""
from censys.search import SearchClient

c = SearchClient()

# The aggregate method constructs a report using a query, an aggregation field, and the
# number of buckets to bin.
report = c.v2.hosts.aggregate(
    "service.service_name: HTTP",
    "services.port",
    num_buckets=5,
)
print(report)
