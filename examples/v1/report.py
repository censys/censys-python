"""View specific certificate."""
from censys.search import SearchClient

c = SearchClient()

res = c.v1.certificates.report(
    "github.com and tags: trusted", "parsed.validity.start", 5
)
print(res)
