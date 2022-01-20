"""Example using SearchClient."""
from censys.search import SearchClient

c = SearchClient()

# v2 indexes
hosts = c.v2.hosts  # Same as hosts = CensysHosts()

# v1 indexes
certs = c.v1.certificates  # Same as certs = CensysCertificates()

data = c.v1.data  # Same as data = CensysData()
