"""Retrieve host risks and subsequent host info for each host risk."""
from censys.asm import HostsAssets, Logbook

logbook = Logbook()
hosts = HostsAssets()

cursor = logbook.get_cursor(filters=["HOST_RISK"])
events = logbook.get_events(cursor)

for event in events:
    # only show logbook events with the 'add' tag
    if event["operation"] == "ADD":
        print(event)

        # enrich the data of this host_risk with more data from the host itself
        host = hosts.get_asset_by_id(event["entity"]["ipAddress"])
        print(host)
