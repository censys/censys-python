"""View specific certificate."""
from censys.search import SearchClient

c = SearchClient()

res = c.v1.websites.report(
    ' "welcome to" AND tags.raw: "http" ', "80.http.get.headers.server.raw", 5
)
print(res)
