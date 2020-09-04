import censys.websites

c = censys.websites.CensysWebsites(api_id="XXX", api_secret="XXX")

# The report method constructs a report using a query, an aggregation field, and the
# number of buckets to bin.
websites = c.report(
    """ "welcome to" AND tags.raw: "http" """,
    field="80.http.get.headers.server.raw",
    buckets=5,
)
print(websites)