"""Example using SearchClient."""
from censys.search import SearchClient

c = SearchClient()

# v1
certs = c.v1.certificates  # or c.v1.certs

data = c.v1.data

# v2
hosts = c.v2.hosts
