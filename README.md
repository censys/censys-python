# Censys Python Library ![PyPI](https://img.shields.io/pypi/v/censys) ![Python Versions](https://img.shields.io/pypi/pyversions/censys)

This is a lightweight Python wrapper to the Censys REST API. `censys-python` currently supports Python 3.6+.

## Install

The library can be installed using `pip`

```bash
pip install censys
```

## Usage

The Censys Search API provides functionality for interacting with Censys resources such as IPv4 addresses, Websites, and Certificates, and for viewing Account information such as query quota.

There are six API options that this library provides access to:

- `search` - Allows searches against the IPv4 addresses, Websites, and Certificates indexes using the same search syntax as the [web app](https://censys.io/ipv4).
- `view` - Returns the structured data we have about a specific IPv4 address, Website, or Certificate, given the resource's natural id.
- `report` - Allows you view resources as a spectrum based on attributes of the resource, similar to the [Report Builder page](https://censys.io/ipv4/report) on the web app.
- `data` - Returns collections of scan series whose metadata includes a description of the data collected in the series and links to the individual scan results.
- `account` - Returns information about your Censys account, including your current query quota usage. This function is available for all index types.
- `bulk` - Returns the structured data for certificates in bulk, given the certificates' SHA-256 fingerprints.

More details about each option can be found in the Censys API documentation: <https://censys.io/api>.
A list of index fields can be found in the Censys API definitions page: <https://censys.io/ipv4/help/definitions>.

Python class objects must be initialized for each resource index (IPv4 addresses, Websites, and Certificates).

- `CensysIPv4`
- `CensysWebsites`
- `CensysCertificates`

### `search`

**Available in all indexes**

Below we show an example using the `CensysIPv4` index.

```python
import censys.ipv4

c = censys.ipv4.CensysIPv4(api_id="XXX", api_secret="XXX")

for result in c.search(
    "443.https.get.headers.server: Apache AND location.country: Japan", max_records=10
):
    print(result)

# You can optionally restrict the (resource-specific) fields to be
# returned in the matching results. Default behavior is to return a map
# including `location` and `protocol`.
fields = [
    "ip",
    "updated_at",
    "443.https.get.title",
    "443.https.get.headers.server",
    "443.https.get.headers.x_powered_by",
    "443.https.get.metadata.description",
    "443.https.tls.certificate.parsed.subject_dn",
    "443.https.tls.certificate.parsed.names",
    "443.https.tls.certificate.parsed.subject.common_name",
]

data = list(
    c.search(
        "443.https.get.headers.server: Apache AND location.country: Japan",
        fields,
        max_records=10,
    )
)
print(data)
```

### `view`

**Available in all indexes**

Below we show an example using the `CensysCertificates` index.

```python
import censys.certificates

c = censys.certificates.CensysCertificates(api_id="XXX", api_secret="XXX")

# View specific certificate
cert = c.view("a762bf68f167f6fbdf2ab00fdefeb8b96f91335ad6b483b482dfd42c179be076")
print(cert)
```

### `report`

**Available in all indexes**

```python
import censys.websites

c = censys.websites.CensysWebsites(api_id="XXX", api_secret="XXX")

# The report method constructs a report using a query, an aggregation field, and the
# number of buckets to bin.
websites = c.report(
    """ "welcome to" AND tags.raw: "http" """,
    field="80.http.get.headers.server.raw",
    buckets=5,
)
print(websites)
```

### `data`

**Available in all indexes**

### `account`

**Available in all indexes**

### `bulk`

**Available only in the certificate index**

<!-- PROGRESS TO HERE -->

The index APIs allow you to perform full-text searches, view specific records,
and generate aggregate reports about the IPv4, Websites, and Certificates
endpoints.

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
import censys.websites

c = censys.websites.CensysWebsites(api_id="XXX", api_secret="XXX")

# the report method constructs a report using a query, an aggregation field, and the
# number of buckets to bin
c.report(
    """ "welcome to" AND tags.raw: "http" """,
    field="80.http.get.headers.server.raw",
    buckets=5,
)

# the view method lets you see the full JSON for an website
c.view("google.com")

# the search method lets you search the index using indexed fields, full text, and
# combined predicates
for result in c.search(
    "80.http.get.headers.server: Apache", max_records=10
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
        "80.http.get.headers.server: Apache",
        WEBSITE_FIELDS,
        max_records=10,
    )
)
print(data)
```

## Developing

Install dev dependencies with:

```bash
pip install -e .[dev]
```

## Testing

Testing requires both `CENSYS_API_ID` and `CENSYS_API_SECRET` environment variables

```bash
CENSYS_API_ID=xxx CENSYS_API_SECRET=xxx pytest
```
