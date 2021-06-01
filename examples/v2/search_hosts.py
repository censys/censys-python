"""Search hosts data set."""
from pprint import pprint

from censys.search import SearchClient

c = SearchClient()

# Single page of search results
query = c.v2.hosts.search("service.service_name: HTTP", per_page=5)
print(query())

# Multiple pages of search results
query = c.v2.hosts.search("service.service_name: HTTP", per_page=5, pages=2)
for page in query:
    print(page)

# View all results
query = c.v2.hosts.search("service.service_name: HTTP", per_page=5, pages=2)
pprint(query.view_all())
