Usage v2
========

The Censys Search API provides functionality for interacting with Censys resources such as Hosts.

There are three API options that this library provides access to:

-  :attr:`search <censys.search.v2.api.CensysSearchAPIv2.search>` - Allows searches against the Hosts index using the same search syntax as the `web app <https://search.censys.io/search/language?resource=hosts>`__.
-  :attr:`view <censys.search.v2.api.CensysSearchAPIv2.view>` - Returns the structured data we have about a specific Host, given the resource's natural ID.
-  :attr:`aggregate <censys.search.v2.api.CensysSearchAPIv2.aggregate>` - Allows you to view resources as a spectrum based on attributes of the resource, similar to the `Report Builder page <https://search.censys.io/search/report?resource=hosts>`__ on the web app.

More details about each option can be found in the `Censys API documentation <https://search.censys.io/api>`__. A list of index fields can be found in the `Censys API definitions page <https://search.censys.io/api>`__.

Python class objects must be initialized for each resource index (Hosts).

-  :attr:`CensysHosts <censys.search.v2.CensysHosts>`

``search``
----------

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. code:: python

    from censys.search import CensysHosts

    h = CensysHosts()

    # Single page of search results
    query = h.search("service.service_name: HTTP", per_page=5)
    print(query())

    # Multiple pages of search results
    # You can optionally pass in a number of results to be returned
    # each page and the number of pages you want returned.
    for page in h.search("service.service_name: HTTP", per_page=5, pages=2):
        print(page)

    # View each result returned
    # For `hosts` this looks like a mapping of IPs to view results
    query = h.search("service.service_name: HTTP", per_page=5, pages=2)
    print(query.view_all())

``view``
--------

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. code:: python

    from censys.search import CensysHosts

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

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. code:: python

    from censys.search import CensysHosts

    h = CensysHosts()

    # The aggregate method constructs a report using a query, an aggregation field, and the
    # number of buckets to bin.
    report = h.aggregate(
        "service.service_name: HTTP",
        "services.port",
        num_buckets=5,
    )
    print(report)

``view_host_names``
-------------------

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. code:: python

    from censys.search import CensysHosts

    h = CensysHosts()

    # Fetch a list of host names for the specified IP address.
    names = h.view_host_names("1.1.1.1")
    print(names)
    
``view_host_events``
--------------------

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. code:: python

    from censys.search import CensysHosts

    h = CensysHosts()

    # Fetch a list of events for the specified IP address.
    events = h.view_host_events("1.1.1.1")
    print(events)

    # You can also pass in a date or datetime objects.
    from datetime import date
    events = h.view_host_events("1.1.1.1", start_time=date(2021, 7, 1), end_time=date(2021, 7, 31))
    print(events)

``metadata``
-------------

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. code:: python

    from censys.search import CensysHosts

    h = CensysHosts()

    # Fetch metadata about hosts.
    meta = h.metadata()
    print(meta.get("services"))
