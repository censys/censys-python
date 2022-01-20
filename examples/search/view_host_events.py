"""View host events."""
from censys.search import CensysHosts

h = CensysHosts()

# Fetch a list of events for the specified IP address.
events = h.view_host_events("1.1.1.1")
print(events)

# You can also pass in a date or datetime objects.
from datetime import date

events = h.view_host_events(
    "1.1.1.1", start_time=date(2022, 1, 1), end_time=date(2022, 1, 31)
)
print(events)
# [
#     {
#         "timestamp": "2022-01-01T00:00:01.713Z",
#         "service_observed": {
#             "id": {"port": 80, "service_name": "HTTP", "transport_protocol": "TCP"},
#             "observed_at": "2021-12-31T23:59:39.910804158Z",
#             "perspective_id": "PERSPECTIVE_NTT",
#             "changed_fields": [
#                 {"field_name": "http.request.uri"},
#                 {"field_name": "http.response.headers.Cf-Ray.headers"},
#                 {"field_name": "http.response.headers.Location.headers"},
#                 {"field_name": "banner"},
#             ],
#         },
#         "_event": "service_observed",
#     },
#     ...
# ]
