"""Example using SearchClient."""
from censys.search import SearchClient

c = SearchClient()

# v2 indexes
hosts = c.v2.hosts  # Same as hosts = CensysHosts()

certs = c.v2.certificates  # Same as certs = CensysCerts()

# v1 indexes
data = c.v1.data  # Same as data = CensysData()
