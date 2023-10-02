"""View host certificates."""
from censys.search import CensysHosts

h = CensysHosts()

# Fetch a list of certificates for the specified IP address.
certificates = h.view_host_certificates("1.1.1.1")
# print(certificates)

# You can also pass in a date or datetime objects.
from datetime import date

certificates = h.view_host_certificates(
    "1.1.1.1", per_page=1, start_time=date(2023, 1, 1)
)
print(certificates)
# {
#     "ip": "1.1.1.1",
#     "certificates": [
#         {
#             "fingerprint": "string",
#             "port": 0,
#             "service_name": "string",
#             "transport_protocol": "TCP",
#             "first_observed_at": "2023-10-02T13:32:26.202Z",
#             "last_observed_at": "2023-10-02T13:32:26.202Z",
#             "first_updated_at": "2023-10-02T13:32:26.202Z",
#             "last_updated_at": "2023-10-02T13:32:26.202Z",
#         },
#         ...
#     ],
#     "links": {"next": "nextCursorToken"},
# }
