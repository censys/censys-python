"""View specific certificate."""

from censys.search import CensysCerts

c = CensysCerts()

res = c.aggregate("parsed.subject.country: AU", "parsed.issuer.organization", 5)
print(res)
