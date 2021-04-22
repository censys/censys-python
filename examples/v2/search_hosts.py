"""Search hosts data set."""
from censys import CensysHosts

h = CensysHosts()

# Single page of search results
query = h.search("service.service_name: HTTP", per_page=5)
print(query())

# Multiple pages of search results
query = h.search("service.service_name: HTTP", per_page=5, pages=2)
for page in query:
    print(page)
