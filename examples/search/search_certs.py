"""Search certificate data set."""
from censys.search import CensysCerts

c = CensysCerts()


# Single page of search results
query = c.search(
    "parsed.subject.country: AU",
    fields=[
        "names",
        "fingerprint_sha256",
        "parsed.issuer.organization",
        "parsed.subject.postal_code",
    ],
    sort=["parsed.issuer.organization", "parsed.subject.postal_code"],
)
hits = query()
print(hits)

# Multiple pages of search results
query = c.search(
    "parsed.subject.country: AU",
    fields=[
        "names",
        "fingerprint_sha256",
        "parsed.issuer.organization",
        "parsed.subject.postal_code",
    ],
    sort=["parsed.issuer.organization", "parsed.subject.postal_code"],
    pages=2,
    per_page=5,
)
for hits in query:
    for hit in hits:
        print(hit)

# View all results
query = c.search(
    "parsed.subject.country: AU",
    fields=[
        "names",
        "fingerprint_sha256",
        "parsed.issuer.organization",
        "parsed.subject.postal_code",
    ],
    sort=["parsed.issuer.organization", "parsed.subject.postal_code"],
    pages=2,
    per_page=5,
)
print(query.view_all())
