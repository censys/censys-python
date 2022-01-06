"""Search certificate data set."""
from censys.search import CensysCertificates

c = CensysCertificates()

fields = ["parsed.subject_dn", "parsed.fingerprint_sha256", "parsed.fingerprint_sha1"]

for cert in c.search("validation.nss.valid: true", fields, max_records=5):
    print(cert["parsed.subject_dn"])
