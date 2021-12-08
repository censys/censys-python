Usage v1
========

The Censys Search API provides functionality for interacting with Censys resources such as Certificates, and for viewing Account information such as query quota.

There are six API options that this library provides access to:

-  :attr:`search <censys.search.v1.api.CensysSearchAPIv1.search>` - Allows searches against the Certificates indexes using the same search syntax as the `web app <https://search.censys.io/certificates>`__.
-  :attr:`view <censys.search.v1.api.CensysSearchAPIv1.view>` - Returns the structured data we have about a specific Certificate, given the resource's natural ID.
-  :attr:`report <censys.search.v1.api.CensysSearchAPIv1.report>` - Allows you to view resources as a spectrum based on attributes of the resource, similar to the `Report Builder page <https://search.censys.io/certificates/report>`__ on the web app.
-  :attr:`data <censys.search.v1.CensysData>` - Returns collections of scan series whose metadata includes a description of the data collected in the series and links to the individual scan results.
-  :attr:`account <censys.search.v1.api.CensysSearchAPIv1.account>` - Returns information about your Censys account, including your current query quota usage. This function is available for all index types.
-  :attr:`bulk <censys.search.v1.CensysCertificates.bulk>` - Returns the structured data for certificates in bulk, given the certificates' SHA-256 fingerprints.

More details about each option can be found in the `Censys API documentation <https://search.censys.io/api>`__. A list of index fields can be found in the `Censys API definitions page <https://search.censys.io/certificates/help>`__.

Python class objects must be initialized for each resource index (Certificates).

-  :attr:`CensysCertificates <censys.search.v1.CensysCertificates>`
-  :attr:`CensysData <censys.search.v1.CensysData>`

``search``
----------

Below we show an example using the :attr:`CensysCertificates <censys.search.v1.CensysCertificates>` index.

.. code:: python

    from censys.search import CensysCertificates

    c = CensysCertificates()

    for page in c.search(
        "validation.nss.valid: true and validation.nss.type: intermediate", 
        max_records=10
    ):
        print(page)

    # You can optionally restrict the (resource-specific) fields to be
    # returned in the matching results. Default behavior is to return a map
    # including `location` and `protocol`.
    fields = [
        "fingerprint_sha256",
        "parsed.validity.start",
        "parsed.validity.end",
        "parsed.subject_dn",
        "parsed.names",
        "parsed.subject.common_name",
    ]

    for page in c.search(
            "censys.io and tags: trusted",
            fields,
            max_records=10,
        ):
        print(page)

``view``
--------

Below we show an example using the :attr:`CensysCertificates <censys.search.v1.CensysCertificates>` index.

.. code:: python

    from censys.search import CensysCertificates

    c = CensysCertificates()

    # View specific certificate
    cert = c.view("a762bf68f167f6fbdf2ab00fdefeb8b96f91335ad6b483b482dfd42c179be076")
    print(cert)

``report``
----------

Below we show an example using the :attr:`CensysCertificates <censys.search.v1.CensysCertificates>` index.

.. code:: python

    from censys.search import CensysCertificates

    c = CensysCertificates()

    # The report method constructs a report using a query, an aggregation field, and the
    # number of buckets to bin.
    certificates = c.report(
        """censys.io and tags: trusted""",
        field="parsed.version",
        buckets=5,
    )
    print(certificates)

``data``
--------

Below we show an example using the :attr:`CensysData <censys.search.v1.CensysData>` index.

.. code:: python

    from censys.search import CensysData

    c = CensysData()

    # View a specific result from a specific series
    result = c.view_result("ipv4_2018", "20200818")
    print(result)

``account``
-----------

Below we show an example using the :attr:`CensysCertificates <censys.search.v1.CensysCertificates>` index.

.. code:: python

    from censys.search import CensysCertificates

    c = CensysCertificates()

    # Gets account data
    account = c.account()
    print(account)

    # Gets account quota
    quota = c.quota()
    print(quota)

``bulk``
--------

**Please note this method is only available only for the CensysCertificates index**

Below we show an example using the :attr:`CensysCertificates <censys.search.v1.CensysCertificates>` index.

.. code:: python

    from censys.search import CensysCertificates

    c = CensysCertificates()

    fingerprints = [
        "fce621c0dc1c666d03d660472f636ce91e66e96460545f0da7eb1a24873e2f70",
        "a762bf68f167f6fbdf2ab00fdefeb8b96f91335ad6b483b482dfd42c179be076"
    ]

    # Get bulk certificate data
    certs = c.bulk(fingerprints)
    print(certs)
