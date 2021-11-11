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

    # You can also get all pages of results by using -1 for pages
    for page in h.search("service.service_name: HTTP", pages=-1):
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

``metadata``
-------------

**Please note this method is only available only for the CensysHosts index**

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. code:: python

    from censys.search import CensysHosts

    h = CensysHosts()

    # Fetch metadata about hosts.
    meta = h.metadata()
    print(meta.get("services"))

``view_host_names``
-------------------

**Please note this method is only available only for the CensysHosts index**

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. code:: python

    from censys.search import CensysHosts

    h = CensysHosts()

    # Fetch a list of host names for the specified IP address.
    names = h.view_host_names("1.1.1.1")
    print(names)
    
``view_host_events``
--------------------

**Please note this method is only available only for the CensysHosts index**

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

``get_hosts_by_cert``
---------------------

**Please note this method is only available only for the CensysCerts index**

Below we show an example using the :attr:`CensysCerts <censys.search.v2.CensysCerts>` index.

.. code:: python

    from censys.search import CensysCerts

    c = CensysCerts()

    # Fetch a list of events for the specified IP address.
    hosts, links = c.get_hosts_by_cert("fb444eb8e68437bae06232b9f5091bccff62a768ca09e92eb5c9c2cf9d17c426")
    print(hosts)

Comments
--------

``get_comments``
^^^^^^^^^^^^^^^^

Below we show an example using the :attr:`CensysCerts <censys.search.v2.CensysCerts>` index.

.. code:: python

    from censys.search import CensysCerts

    c = CensysCerts()

    # Fetch a list of comments for the specified certificate.
    comments = c.get_comments("fb444eb8e68437bae06232b9f5091bccff62a768ca09e92eb5c9c2cf9d17c426")
    print(comments)

``add_comment``
^^^^^^^^^^^^^^^^

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. code:: python

    from censys.search import CensysHosts

    h = CensysHosts()

    # Add a comment to a host.
    comment = h.add_comment("1.1.1.1", "This is a test comment")
    print(comment)

``update_comment``
^^^^^^^^^^^^^^^^^^

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. code:: python

    from censys.search import CensysHosts

    h = CensysHosts()

    # Update a comment to a host.
    comment = h.update_comment("1.1.1.1", 101, "This is an updated test comment")

``delete_comment``
^^^^^^^^^^^^^^^^^^

Below we show an example using the :attr:`CensysCerts <censys.search.v2.CensysCerts>` index.

.. code:: python

    from censys.search import CensysCerts

    c = CensysCerts()

    # Delete a comment for a certificate.
    c.delete_comment("fb444eb8e68437bae06232b9f5091bccff62a768ca09e92eb5c9c2cf9d17c426", 102)

Tags
----

``list_all_tags``
^^^^^^^^^^^^^^^^^

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. code:: python

    from censys.search import CensysHosts

    h = CensysHosts()

    # Fetch a list of all tags.
    tags = h.list_all_tags()
    print(tags)

``create_tag``
^^^^^^^^^^^^^^

Below we show an example using the :attr:`CensysCerts <censys.search.v2.CensysCerts>` index.

.. code:: python

    from censys.search import CensysCerts

    c = CensysCerts()

    # Create a new tag.
    tag = c.create_tag("test-tag")
    print(tag)

    # Optionally you can specify a color for the tag.
    tag = c.create_tag("test-tag", color="#00FF00")
    print(tag)

``get_tag``
^^^^^^^^^^^

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. code:: python

    from censys.search import CensysHosts

    h = CensysHosts()

    # Fetch a tag.
    tag = h.get_tag("123")
    print(tag)

``update_tag``
^^^^^^^^^^^^^^

Below we show an example using the :attr:`CensysCerts <censys.search.v2.CensysCerts>` index.

.. code:: python

    from censys.search import CensysCerts

    c = CensysCerts()

    # Update a tag.
    tag = c.update_tag("123", "test-tag")
    print(tag)

    # Optionally you can specify a color for the tag.
    tag = c.update_tag("123", "test-tag", color="#00FF00")
    print(tag)

``delete_tag``
^^^^^^^^^^^^^^

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. code:: python

    from censys.search import CensysHosts

    h = CensysHosts()

    # Delete a tag.
    h.delete_tag("123)

``list_tags_on_document``
^^^^^^^^^^^^^^^^^^^^^^^^^

Below we show an example using the :attr:`CensysCerts <censys.search.v2.CensysCerts>` index.

.. code:: python

    from censys.search import CensysCerts

    c = CensysCerts()

    # Fetch a list of tags for a document.
    tags = c.list_tags_on_document("fb444eb8e68437bae06232b9f5091bccff62a768ca09e92eb5c9c2cf9d17c426")
    print(tags)

``add_tag_to_document``
^^^^^^^^^^^^^^^^^^^^^^^

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. code:: python

    from censys.search import CensysHosts

    h = CensysHosts()

    # Add a tag to a document.
    h.add_tag_to_document("123)

``remove_tag_from_document``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Below we show an example using the :attr:`CensysCerts <censys.search.v2.CensysCerts>` index.

.. code:: python

    from censys.search import CensysCerts

    c = CensysCerts()

    # Remove a tag from a document.
    c.remove_tag_from_document("fb444eb8e68437bae06232b9f5091bccff62a768ca09e92eb5c9c2cf9d17c426")

``list_certs_with_tag``
^^^^^^^^^^^^^^^^^^^^^^^

**Please note this method is only available only for the CensysCerts index**

Below we show an example using the :attr:`CensysCerts <censys.search.v2.CensysCerts>` index.

.. code:: python

    from censys.search import CensysCerts

    c = CensysCerts()

    # Fetch a list of certs with the specified tag.
    certs = c.list_certs_with_tag("123")
    print(certs)

``list_hosts_with_tag``
^^^^^^^^^^^^^^^^^^^^^^^

**Please note this method is only available only for the CensysHosts index**

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. code:: python

    from censys.search import CensysHosts

    h = CensysHosts()

    # Fetch a list of hosts with the specified tag.
    hosts = h.list_hosts_with_tag("123")
    print(hosts)
