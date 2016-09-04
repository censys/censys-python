Censys Python Library
=====================

This is a light weight Python wrapper to the Censys REST API.

Install
-------

The egg can be installed using Pip or easy_install (e.g., `sudo pip install censys`). Once installed, you can

Usage
=====

There are three API endpoints that the library provides access to:


Index API
---------

The index APIs allow you to perform full-text searches, view specific records,
and generate aggregate reports about the IPv4, Websites, and Certificates
endpoints. There is a python class for each index: `CensysIPv4`,
`CensysWebsites`, and `CensysCertificates`. Below, we show an example for
certificates, but the same methods exist for each of the three indices.
```python
import censys.certificates

c = censys.certificates.CensysCertificates(api_id="XXX", api_secret="XXX")

# view specific certificate
print c.view("a762bf68f167f6fbdf2ab00fdefeb8b96f91335ad6b483b482dfd42c179be076")

# iterate over certificates that match a search
for cert in c.search("github.com and valid_nss: true", fields=["parsed.subject_dn", parsed.fingerprint_sha256]):
	print cert

```

Query API
---------

Export API
----------




Index APIs
