"""View specific host."""
from datetime import date

from censys.search import SearchClient

c = SearchClient()

# Fetch a specific host and its services
host = c.v2.hosts.view("8.8.8.8")
print(host)

# You can optionally pass in a RFC3339 timestamp to
# fetch a host at the given point in time.
# Please note historical API access is required.
host = c.v2.hosts.view("8.8.8.8", at_time="2021-03-01T17:49:05Z")
print(host)

# You can also pass in a date or datetime object.
host = c.v2.hosts.view("8.8.8.8", at_time=date(2021, 3, 1))
print(host)
