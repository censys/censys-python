"""Example using SearchClient."""
from censys import SearchClient

c = SearchClient()

# v1
certs = c.v1.certificates

data = c.v1.data

ipv4 = c.v1.ipv4

websites = c.v1.websites

# v2
hosts = c.v2.hosts
