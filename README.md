# Censys Python Library ![PyPI](https://img.shields.io/pypi/v/censys) ![Python Versions](https://img.shields.io/pypi/pyversions/censys) [![License](https://img.shields.io/github/license/censys/censys-python)](LICENSE) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

An easy-to-use and lightweight API wrapper for the Censys Search Engine ([censys.io](https://censys.io/)). Python 3.6+ is currently supported.

## Getting Started

The library can be installed using `pip`.

```bash
$ pip install censys
```

To configure your credentials run `censys config` or set both `CENSYS_API_ID` and `CENSYS_API_SECRET` environment variables.

```bash
$ censys config

Censys API ID: XXX
Censys API Secret: XXX

Successfully authenticated for your@email.com
```

## Usage

The Censys Search API provides functionality for interacting with Censys resources such as IPv4 addresses, Websites, and Certificates, and for viewing Account information such as query quota.

There are six API options that this library provides access to:

- `search` - Allows searches against the IPv4 addresses, Websites, and Certificates indexes using the same search syntax as the [web app](https://censys.io/ipv4).
- `view` - Returns the structured data we have about a specific IPv4 address, Website, or Certificate, given the resource's natural ID.
- `report` - Allows you to view resources as a spectrum based on attributes of the resource, similar to the [Report Builder page](https://censys.io/ipv4/report) on the web app.
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

Below we show an example using the `CensysIPv4` index.

```python
import censys.ipv4

c = censys.ipv4.CensysIPv4(api_id="XXX", api_secret="XXX")

for page in c.search(
    "443.https.get.headers.server: Apache AND location.country: Japan", max_records=10
):
    print(page)

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

for page in c.search(
        "443.https.get.headers.server: Apache AND location.country: Japan",
        fields,
        max_records=10,
    ):
    print(page)
```

### `view`

Below we show an example using the `CensysCertificates` index.

```python
import censys.certificates

c = censys.certificates.CensysCertificates(api_id="XXX", api_secret="XXX")

# View specific certificate
cert = c.view("a762bf68f167f6fbdf2ab00fdefeb8b96f91335ad6b483b482dfd42c179be076")
print(cert)
```

### `report`

Below we show an example using the `CensysWebsites` index.

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

Below we show an example using the `CensysData` index.

```python
import censys.data

c = censys.data.CensysData(api_id="XXX", api_secret="XXX")

# View a specific result from a specific series
result = c.view_result("ipv4_2018", "20200818")
print(result)
```

### `account`

Below we show an example using the `CensysIPv4` index.

```python
import censys.ipv4

c = censys.ipv4.CensysIPv4(api_id="XXX", api_secret="XXX")

# Gets account data
c.account()

# Gets account quota
c.quota()
```

### `bulk`

**Please note this method is only available only for the certificate index**

Below we show an example using the `CensysCertificates` index.

```python
import censys.certificates

c = censys.certificates.CensysCertificates(api_id="XXX", api_secret="XXX")

fingerprints = [
    "fce621c0dc1c666d03d660472f636ce91e66e96460545f0da7eb1a24873e2f70",
    "a762bf68f167f6fbdf2ab00fdefeb8b96f91335ad6b483b482dfd42c179be076"
]

# Get bulk certificate data
certs = c.bulk(fingerprints)
print(certs)
```

## CLI Usage

### Search

```bash
$ censys search --help

usage: censys search [-h] [--api-id API_ID] [--api-secret API_SECRET] -q QUERY
                     [--index-type ipv4|certs|websites]
                     [--fields FIELDS [FIELDS ...]] [--overwrite]
                     [-f json|csv|screen] [-o OUTPUT]
                     [--start-page START_PAGE] [--max-pages MAX_PAGES]

Query Censys Search for resource data by providing a query string, the
resource index, and the fields to be returned

optional arguments:
  -h, --help            show this help message and exit
  --api-id API_ID       a Censys API ID (alternatively you can use the env
                        variable CENSYS_API_ID)
  --api-secret API_SECRET
                        a Censys API SECRET (alternatively you can use the env
                        variable CENSYS_API_SECRET)
  -q QUERY, --query QUERY
                        a string written in Censys Search syntax
  --index-type ipv4|certs|websites
                        which resource index to query
  --fields FIELDS [FIELDS ...]
                        list of index-specific fields
  --overwrite           overwrite instead of append fields returned by default
                        with fields provided in the fields argument
  -f json|csv|screen, --format json|csv|screen
                        format of output
  -o OUTPUT, --output OUTPUT
                        output file path
  --start-page START_PAGE
                        page number to start from
  --max-pages MAX_PAGES
                        maximum number of pages of results to return
```

### HNRI

```bash
$ censys hnri --help

usage: censys hnri [-h] [--api-id API_ID] [--api-secret API_SECRET]

Home Network Risk Identifier (H.N.R.I.)

optional arguments:
  -h, --help            show this help message and exit
  --api-id API_ID       a Censys API ID (alternatively you can use the env
                        variable CENSYS_API_ID)
  --api-secret API_SECRET
                        a Censys API SECRET (alternatively you can use the env
                        variable CENSYS_API_SECRET)
```

## Resources

- [Official Website](https://censys.io/)
<!-- - [Documentation]() -->
- [Issue Tracker](https://github.com/censys/censys-python/issues)

## Contributing

All contributions (no matter if small) are always welcome.

### Getting started

```bash
$ git clone git@github.com:censys/censys-python.git
$ pip install -e .[dev]
```

### Testing

Testing requires credentials to be set.

```bash
$ pytest
```
