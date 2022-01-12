"""View Host Diff."""
from datetime import date

from censys.search import CensysHosts

c = CensysHosts()

# Compare a single host between two timestamps
diff = c.view_host_diff("1.1.1.1", at_time=date(2022, 1, 1), at_time_b=date(2022, 1, 2))
print(diff)

# Compare a single host between its current timestamp and a timestamp
diff = c.view_host_diff("1.1.1.2", at_time=date(2022, 1, 2))
print(diff)

# Compare two hosts
diff = c.view_host_diff("1.1.1.1", ip_b="1.1.1.2")
print(diff)

# Compare two hosts between two timestamps
diff = c.view_host_diff(
    "1.1.1.1",
    ip_b="1.1.1.2",
    at_time=date(2022, 1, 1),
    at_time_b=date(2022, 1, 2),
)
print(diff)
