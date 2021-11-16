from censys.asm import Events
from censys.asm import HostsAssets

# --- functions ---


# --- main thread ---

# it is worth noting that there will be an API endpoint soon at "/api/v2/risks" that will have full filtering capabilities for risks
# until then, we can grab host risks via the logbook and then enrich that using asset info (https://censys-python.readthedocs.io/en/stable/usage-asm.html#assets)
e = Events()
h = HostsAssets()

cursor = e.get_cursor(filters=["HOST_RISK"])
# print(cursor)
events = e.get_events(cursor)

for event in events:
    # only show logbook events with the 'add' tag
    if event["operation"] == 'ADD':
        print(event)

        # enrich the data of this host_risk with more data from the host itself
        host = h.get_asset_by_id(event["entity"]["ipAddress"])
        print(host)

        # remove this if you want to loop through all host risks
        # break

#consolidate and export to a csv as you wish