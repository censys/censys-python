Usage v1
========

The Censys Search API provides functionality for interacting with Censys resources such as Hosts.

There are three API options that this library provides access to:

-  ``search`` - Allows searches against the Hosts indexes using the same search syntax as the `web app <https://search.censys.io/search/language?resource=hosts>`__.
-  ``view`` - Returns the structured data we have about a specific Host, given the resource's natural ID.
-  ``aggregate`` - Allows you to view resources as a spectrum based on attributes of the resource, similar to the `Report Builder page <https://search.censys.io/search/report?resource=hosts>`__ on the web app.

More details about each option can be found in the Censys API documentation: https://search.censys.io/api. A list of index fields can be found in the Censys API definitions page: https://search.censys.io/api/v2/docs.

Python class objects must be initialized for each resource index (Hosts).

-  ``CensysHosts``

``search``
----------

Below we show an example using the ``CensysHosts`` index.

.. code:: python

    from censys import CensysHosts

    h = CensysHosts()

    # Search for hosts running HTTP
    for host in h.search("service.service_name: HTTP"):
        print(host)

    # You can optionally pass in a number of results to be returned
    # each page and the number of pages you want returned.
    for host in h.search("service.service_name: HTTP", per_page=25, pages=2):
        print(host)

``view``
--------

Below we show an example using the ``CensysHosts`` index.

.. code:: python

    from censys import CensysHosts

    h = CensysHosts()

    # Fetch a specific host and its services
    host = h.view("8.8.8.8")
    print(host)

    # You can optionally pass in a RFC3339 timestamp to
    # fetch a host at the given point in time.
    # Please note historical API access is required.
    host = h.view("8.8.8.8", at_time="2021-03-01T17:49:05Z")
    print(host)

    # You can also pass in a date or datetime object.
    from datetime import date
    host = h.view("8.8.8.8", at_time=date(2021, 3, 1))
    print(host)

``aggregate``
-------------

Below we show an example using the ``CensysHosts`` index.

.. code:: python

    from censys import CensysHosts

    h = CensysHosts()

    # The aggregate method constructs a report using a query, an aggregation field, and the
    # number of buckets to bin.
    report = h.aggregate(
        "service.service_name: HTTP",
        "services.port",
        num_buckets=5,
    )
    print(report)
