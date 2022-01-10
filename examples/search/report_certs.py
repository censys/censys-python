"""View specific certificate."""
from censys.search import CensysCertificates

c = CensysCertificates()

res = c.report("github.com and tags: trusted", "parsed.validity.start", 5)
print(res)
