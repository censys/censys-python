"""View specific host."""
from censys.search import CensysHosts
from datetime import date

h = CensysHosts()

# Fetch a specific host and its services
host = h.view("8.8.8.8")
print(host)

# You can optionally pass in a RFC3339 timestamp to
# fetch a host at the given point in time.
# Please note historical API access is required.
host = h.view("8.8.8.8", at_time="2021-03-01T17:49:05Z")
print(host)

# You can also pass in a date or datetime object.
host = h.view("8.8.8.8", at_time=date(2021, 3, 1))
print(host)
