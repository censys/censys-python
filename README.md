# Censys Python Library ![PyPI](https://img.shields.io/pypi/v/censys) ![PyPI - License](https://img.shields.io/pypi/l/censys)

This is a light weight Python wrapper to the Censys REST API.

## Install

The egg can be installed using Pip or easy_install (e.g., `pip install censys`).

## Usage

There are three API endpoints that the library provides access to: Index,
Query, and Export. More details about each can be found in the Censys API
documentation: <https://censys.io/api>.

## Search/View/Report API

The index APIs allow you to perform full-text searches, view specific records,
and generate aggregate reports about the IPv4, Websites, and Certificates
endpoints. There is a Python class for each index: `CensysCertificates`,
`CensysIPv4`, and `CensysWebsites`.

Below, we show an example for certificates, but the same methods exist for each
of the three indices, with the exception of bulk which is only supported by the certificates index.

```python
import censys.certificates

c = censys.certificates.CensysCertificates(api_id="XXX", api_secret="XXX")

# view specific certificate
print(c.view("a762bf68f167f6fbdf2ab00fdefeb8b96f91335ad6b483b482dfd42c179be076"))

fingerprints = list()
# iterate over certificates that match a search
fields = ["parsed.subject_dn", "parsed.fingerprint_sha256"]
for cert in c.search("github.com and valid_nss: true", fields=fields):
    fingerprints.append(cert["parsed.fingerprint_sha256"])
    print(cert["parsed.subject_dn"])

# get certificates in bulk from a list of fingerprints
print(c.bulk(fingerprints))

# aggregate report on key types used by trusted certificates
print(
    c.report(
        query="valid_nss: true", field="parsed.subject_key_info.key_algorithm.name"
    )
)
```

Here's how to use the IPv4 index.

```python
import censys.ipv4

c = censys.ipv4.CensysIPv4(api_id="XXX", api_secret="XXX")

# the report method constructs a report using a query, an aggregation field, and the
# number of buckets to bin
c.report(
    """ "welcome to" AND tags.raw: "http" """,
    field="80.http.get.headers.server.raw",
    buckets=5,
)

# the view method lets you see the full JSON for an IP address
c.view("8.8.8.8")

# the search method lets you search the index using indexed fields, full text, and
# combined predicates
for result in c.search(
    "80.http.get.headers.server: Apache AND location.country: Japan", max_records=10
):
    print(result)

# you can optionally specify which fields you want to come back for search results
IPV4_FIELDS = [
    "ip",
    "updated_at",
    "80.http.get.title",
    "443.https.get.title",
    "443.https.tls.certificate.parsed.subject_dn",
    "443.https.tls.certificate.parsed.names",
    "443.https.tls.certificate.parsed.subject.common_name",
    "443.https.tls.certificate.parsed.extensions.subject_alt_name.dns_names",
    "25.smtp.starttls.tls.certificate.parsed.names",
    "25.smtp.starttls.tls.certificate.parsed.subject_dn",
    "110.pop3.starttls.tls.certificate.parsed.names",
    "110.pop3.starttls.tls.certificate.parsed.subject_dn",
]

data = list(
    c.search(
        "80.http.get.headers.server: Apache AND location.country: Japan",
        IPV4_FIELDS,
        max_records=10,
    )
)
print(data)
```

Here's how to use the Website index.

```python
import censys.website

c = censys.website.CensysWebsites(api_id="XXX", api_secret="XXX")

# the report method constructs a report using a query, an aggregation field, and the
# number of buckets to bin
c.report(
    """ "welcome to" AND tags.raw: "http" """,
    field="80.http.get.headers.server.raw",
    buckets=5,
)

# the view method lets you see the full JSON for an website
c.view("google.com)

# the search method lets you search the index using indexed fields, full text, and
# combined predicates
for result in c.search(
    "80.http.get.headers.server: Apache AND location.country: Japan", max_records=10
):
    print(result)

# you can optionally specify which fields you want to come back for search results
WEBSITE_FIELDS = [
    "ip",
    "domain",
    "updated_at",
    "80.http.get.title",
    "443.https.get.title",
    "443.https.tls.certificate.parsed.subject_dn",
    "443.https.tls.certificate.parsed.names",
    "443.https.tls.certificate.parsed.subject.common_name",
    "443.https.tls.certificate.parsed.extensions.subject_alt_name.dns_names",
]

data = list(
    c.search(
        "80.http.get.headers.server: Apache AND location.country: Japan",
        WEBSITE_FIELDS,
        max_records=10,
    )
)
print(data)
```
