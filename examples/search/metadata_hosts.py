"""Metadata on the hosts index."""
from censys.search import CensysHosts

h = CensysHosts()

# Fetch metadata about hosts.
meta = h.metadata()
print(meta)
# {
#     "services": [
#         "DNS",
#         "FTP",
#         "HTTP",
#         "POP3",
#         "SMTP",
#         "SSH",
#         ...
#     ]
# }
