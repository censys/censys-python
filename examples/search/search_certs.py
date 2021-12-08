"""Search certificate data set."""
from censys.search import SearchClient

c = SearchClient()

fields = ["parsed.subject_dn", "parsed.fingerprint_sha256", "parsed.fingerprint_sha1"]

for cert in c.v1.certificates.search(
    "validation.nss.valid: true", fields, max_records=5
):
    print(cert["parsed.subject_dn"])
