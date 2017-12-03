Censys Python Library
=====================

This is a light weight Python wrapper to the Censys REST API.

Install
-------

The egg can be installed using Pip or easy_install (e.g., `sudo pip install censys`).

Usage
=====

There are three API endpoints that the library provides access to: Index,
Query, and Export. More details about each can be found in the Censys API
documentation: https://censys.io/api.


Search/View/Report API
----------------------

The index APIs allow you to perform full-text searches, view specific records,
and generate aggregate reports about the IPv4, Websites, and Certificates
endpoints. There is a Python class for each index: `CensysIPv4`,
`CensysWebsites`, and `CensysCertificates`. Below, we show an example for
certificates, but the same methods exist for each of the three indices.
```python
import censys.certificates

c = censys.certificates.CensysCertificates(api_id="XXX", api_secret="XXX")

# view specific certificate
print c.view("a762bf68f167f6fbdf2ab00fdefeb8b96f91335ad6b483b482dfd42c179be076")

# iterate over certificates that match a search
fields = ["parsed.subject_dn", "parsed.fingerprint_sha256"]
for cert in c.search("github.com and valid_nss: true", fields=fields):
	print cert["parsed.subject_dn"]

# aggregate report on key types used by trusted certificates
print c.report(query="valid_nss: true", field="parsed.subject_key_info.key_algorithm.name")

```

Data API
--------

The Data API allows programatic access to the raw data files.

```python
import censys.data

c = censys.data.CensysDat(api_id="XXX", api_secret="XXX")

# Get a Series
ssh_series = c.view_series('22-ssh-banner-full_ipv4')

# View all the files in each scan
for scan in ssh_series['results']['historical']:
    print c.view_result('22-ssh-banner-full_ipv4', scan['id'])
```
