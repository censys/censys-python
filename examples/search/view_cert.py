"""View specific certificate."""
from censys.search import CensysCertificates

c = CensysCertificates()

res = c.view("82689890be745aef821ee4a988a0b81331f714d7301b288976fab36219b1f493")
print(res)
