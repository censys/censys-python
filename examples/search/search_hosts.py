"""Search hosts data set."""

from censys.search import CensysHosts

h = CensysHosts()

# Single page of search results
query = h.search("services.service_name: HTTP", per_page=5)
print(query())

# Multiple pages of search results
query = h.search("services.service_name: HTTP", per_page=5, pages=2)
for page in query:
    for host in page:
        print(host)

# View all results (this will do a lookup for each host returned by the search)
query = h.search("services.service_name: HTTP", per_page=5, pages=2)
print(query.view_all())

# Search for virtual hosts
query = h.search("not services.service_name: HTTP", per_page=5, virtual_hosts="ONLY")
print(query())

# Search including specific fields
query = h.search(
    "not services.service_name: HTTP",
    per_page=5,
    fields=["ip", "services.port", "services.service_name"],
)
print(query())
