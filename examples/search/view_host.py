"""View specific host."""
from censys.search import CensysHosts

h = CensysHosts()

# Fetch a specific host and its services
host = h.view("8.8.8.8")
print(host)

# You can optionally pass in a RFC3339 timestamp to
# fetch a host at the given point in time.
# Please note historical API access is required.
host = h.view("8.8.8.8", at_time="2021-03-01T17:49:05Z")
print(host)

# You can also pass in a date or datetime object.
from datetime import date

host = h.view("8.8.8.8", at_time=date(2021, 3, 1))
print(host)
# {
#     "ip": "8.8.8.8",
#     "services": [
#         {
#             "dns": {
#                 "server_type": "FORWARDING",
#                 "resolves_correctly": False,
#                 "r_code": "UNKNOWN_CODE",
#             },
#             "extended_service_name": "DNS",
#             "observed_at": "2021-02-28T23:58:55.705035895Z",
#             "perspective_id": "PERSPECTIVE_TELIA",
#             "port": 53,
#             "service_name": "DNS",
#             "source_ip": "74.120.14.37",
#             "transport_protocol": "UDP",
#             "truncated": False,
#         },
#         ...,
#     ],
#     "location": {
#         "continent": "North America",
#         "country": "United States",
#         "country_code": "US",
#         "postal_code": "",
#         "timezone": "America/Chicago",
#         "coordinates": {"latitude": 37.751, "longitude": -97.822},
#         "registered_country": "United States",
#         "registered_country_code": "US",
#     },
#     "location_updated_at": "2022-01-20T16:08:47.237933Z",
#     "autonomous_system": {
#         "asn": 15169,
#         "description": "GOOGLE",
#         "bgp_prefix": "8.8.8.0/24",
#         "name": "GOOGLE",
#         "country_code": "US",
#     },
#     "autonomous_system_updated_at": "2022-01-20T16:08:47.237933Z",
#     "dns": {},
#     "last_updated_at": "2021-02-28T23:58:55.765Z",
# }
