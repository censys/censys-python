"""View all hosts for a given query."""
from censys.search import CensysHosts

h = CensysHosts()

# Search for hosts with a specific service
query = h.search("services.service_name: FTP", per_page=1, pages=2)
# View all results
all_hosts = query.view_all()
print(all_hosts)
