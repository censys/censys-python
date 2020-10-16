Usage
=====

The Censys Search API provides functionality for interacting with Censys resources such as IPv4 addresses, Websites, and Certificates, and for viewing Account information such as query quota.

There are six API options that this library provides access to:

-  ``search`` - Allows searches against the IPv4 addresses, Websites, and Certificates indexes using the same search syntax as the `web app <https://censys.io/ipv4>`__.
-  ``view`` - Returns the structured data we have about a specific IPv4 address, Website, or Certificate, given the resource's natural ID.
-  ``report`` - Allows you to view resources as a spectrum based on attributes of the resource, similar to the `Report Builder page <https://censys.io/ipv4/report>`__ on the web app.
-  ``data`` - Returns collections of scan series whose metadata includes a description of the data collected in the series and links to the individual scan results.
-  ``account`` - Returns information about your Censys account, including your current query quota usage. This function is available for all index types.
-  ``bulk`` - Returns the structured data for certificates in bulk, given the certificates' SHA-256 fingerprints.

More details about each option can be found in the Censys API documentation: https://censys.io/api. A list of index fields can be found in the Censys API definitions page: https://censys.io/ipv4/help/definitions.

Python class objects must be initialized for each resource index (IPv4 addresses, Websites, and Certificates).

-  ``CensysIPv4``
-  ``CensysWebsites``
-  ``CensysCertificates``

``search``
----------

Below we show an example using the ``CensysIPv4`` index.

.. code:: python

    import censys.ipv4

    c = censys.ipv4.CensysIPv4()

    for page in c.search(
        "443.https.get.headers.server: Apache AND location.country: Japan", 
        max_records=10
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

``view``
--------

Below we show an example using the ``CensysCertificates`` index.

.. code:: python

    import censys.certificates

    c = censys.certificates.CensysCertificates()

    # View specific certificate
    cert = c.view("a762bf68f167f6fbdf2ab00fdefeb8b96f91335ad6b483b482dfd42c179be076")
    print(cert)

``report``
----------

Below we show an example using the ``CensysWebsites`` index.

.. code:: python

    import censys.websites

    c = censys.websites.CensysWebsites()

    # The report method constructs a report using a query, an aggregation field, and the
    # number of buckets to bin.
    websites = c.report(
        """ "welcome to" AND tags.raw: "http" """,
        field="80.http.get.headers.server.raw",
        buckets=5,
    )
    print(websites)

``data``
--------

Below we show an example using the ``CensysData`` index.

.. code:: python

    import censys.data

    c = censys.data.CensysData()

    # View a specific result from a specific series
    result = c.view_result("ipv4_2018", "20200818")
    print(result)

``account``
-----------

Below we show an example using the ``CensysIPv4`` index.

.. code:: python

    import censys.ipv4

    c = censys.ipv4.CensysIPv4()

    # Gets account data
    account = c.account()
    print(account)

    # Gets account quota
    quota = c.quota()
    print(quota)

``bulk``
--------

**Please note this method is only available only for the certificate index**

Below we show an example using the ``CensysCertificates`` index.

.. code:: python

    import censys.certificates

    c = censys.certificates.CensysCertificates()

    fingerprints = [
        "fce621c0dc1c666d03d660472f636ce91e66e96460545f0da7eb1a24873e2f70",
        "a762bf68f167f6fbdf2ab00fdefeb8b96f91335ad6b483b482dfd42c179be076"
    ]

    # Get bulk certificate data
    certs = c.bulk(fingerprints)
    print(certs)
