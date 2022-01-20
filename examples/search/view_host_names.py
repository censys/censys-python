"""View host names."""
from censys.search import CensysHosts

h = CensysHosts()

# Fetch a list of host names for the specified IP address.
names = h.view_host_names("1.1.1.1")
print(names)
# [
#     "one.one.one.one",
#     ...
# ]
