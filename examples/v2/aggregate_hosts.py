"""Aggregate hosts data set."""
from censys import CensysHosts

h = CensysHosts()

# The aggregate method constructs a report using a query, an aggregation field, and the
# number of buckets to bin.
report = h.aggregate(
    "service.service_name: HTTP",
    "services.port",
    num_buckets=5,
)
print(report)
