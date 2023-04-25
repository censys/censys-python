"""View specific certificate."""
from censys.search import CensysCerts

c = CensysCerts()

certificates = c.bulk_view(
    [
        "82689890be745aef821ee4a988a0b81331f714d7301b288976fab36219b1f493",
        "9b00121b4e85d50667ded1a8aa39855771bdb67ceca6f18726b49374b41f0041",
    ]
)
for certificate in certificates:
    print(certificate["fingerprint_sha256"])
