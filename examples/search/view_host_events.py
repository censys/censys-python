"""View host events."""
from censys.search import CensysHosts

h = CensysHosts()

# Fetch a list of events for the specified IP address.
events = h.view_host_events("1.1.1.1")
print(events)

# You can also pass in a date or datetime objects.
from datetime import date

events = h.view_host_events(
    "1.1.1.1", per_page=1, start_time=date(2022, 1, 1), end_time=date(2022, 1, 31)
)
print(events)
# {
#     'ip': '1.1.1.1',
#     'events': [
#         {
#             'timestamp': '2022-01-01T00:00:01.713Z',
#             'service_observed': {
#                 'id': {'port': 80, 'service_name': 'HTTP', 'transport_protocol': 'TCP'},
#                 'observed_at': '2021-12-31T23:59:39.910804158Z',
#                 'perspective_id': 'PERSPECTIVE_NTT',
#                 'changed_fields': [{'field_name': 'http.request.uri'}, {'field_name': 'http.response.headers.Cf-Ray.headers'}, {'field_name': 'http.response.headers.Location.headers'}, {'field_name': 'banner'}, {'field_name': 'banner_hashes'}]
#             },
#             '_event': 'service_observed'
#         }
#     ],
#     'links': {
#         'next': 'AS-RtkcKDRPshfT6ojz5ubSuyen_J_J2s9VLmJf9WCg7_jGt0KdU2JvoYW9QXof1Cskvm-b41QyRiR38kWADJuUA_w8rAA5ZNv9llYarhmPv22nIf88JFGGhH0h6dRZ7kDy5RfsiUxNFXeMQQXz0BWYrcQ=='
#     }
# }
