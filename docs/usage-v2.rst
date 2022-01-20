Usage v2
========

The Censys Search API provides functionality for interacting with Censys resources such as Hosts.

There are three main API endpoints that this library provides access to:

-  :attr:`search <censys.search.v2.api.CensysSearchAPIv2.search>` - Allows searches against the Hosts index using the same search syntax as the `web app <https://search.censys.io/search/language?resource=hosts>`__.
-  :attr:`view <censys.search.v2.api.CensysSearchAPIv2.view>` - Returns the structured data we have about a specific Host, given the resource's natural ID.
-  :attr:`aggregate <censys.search.v2.api.CensysSearchAPIv2.aggregate>` - Allows you to view resources as a spectrum based on attributes of the resource, similar to the `Report Builder page <https://search.censys.io/search/report?resource=hosts>`__ on the web app.

More details about each option can be found in the `Censys API documentation <https://search.censys.io/api>`__. A list of index fields can be found in the `Censys API definitions page <https://search.censys.io/api>`__.

Python class objects must be initialized for each resource index (Hosts).

-  :attr:`CensysHosts <censys.search.v2.CensysHosts>`

.. note::

   Please note that the Censys Search v2 API does not support searching, viewing, or aggregating the Certificates index. Please use the :ref:`CensysCertificates (v1) index <usage-v1:Usage v1>` for this functionality.


``search``
----------

**Please note this method is only available only for the CensysHosts index.**

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. include:: ../examples/search/search_hosts.py
   :literal:

``view``
--------

**Please note this method is only available only for the CensysHosts index.**

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. include:: ../examples/search/view_host.py
   :literal:

``bulk_view``
-------------

**Please note this method is only available only for the CensysHosts index.**

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. include:: ../examples/search/bulk_view_hosts.py
   :literal:

``aggregate``
-------------

**Please note this method is only available only for the CensysHosts index.**

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. include:: ../examples/search/aggregate_hosts.py
   :literal:

``metadata``
-------------

**Please note this method is only available only for the CensysHosts index.**

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. include:: ../examples/search/metadata_hosts.py
   :literal:

``view_host_names``
-------------------

**Please note this method is only available only for the CensysHosts index.**

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. include:: ../examples/search/view_host_names.py
   :literal:

``view_host_events``
--------------------

**Please note this method is only available only for the CensysHosts index.**

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. include:: ../examples/search/view_host_events.py
   :literal:

``view_host_diff``
------------------

**Please note this method is only available only for the CensysHosts index.**

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. include:: ../examples/search/view_host_diff.py
    :literal:


``get_hosts_by_cert``
---------------------

**Please note this method is only available only for the CensysCerts index**

Below we show an example using the :attr:`CensysCerts <censys.search.v2.CensysCerts>` index.

.. code:: python

    from censys.search import CensysCerts

    c = CensysCerts()

    # Fetch a list of events for the specified IP address.
    hosts, links = c.get_hosts_by_cert(
        "fb444eb8e68437bae06232b9f5091bccff62a768ca09e92eb5c9c2cf9d17c426"
    )
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
    comments = c.get_comments(
        "fb444eb8e68437bae06232b9f5091bccff62a768ca09e92eb5c9c2cf9d17c426"
    )
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
    c.delete_comment(
        "fb444eb8e68437bae06232b9f5091bccff62a768ca09e92eb5c9c2cf9d17c426", 102
    )

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
    h.delete_tag("123")

``list_tags_on_document``
^^^^^^^^^^^^^^^^^^^^^^^^^

Below we show an example using the :attr:`CensysCerts <censys.search.v2.CensysCerts>` index.

.. code:: python

    from censys.search import CensysCerts

    c = CensysCerts()

    # Fetch a list of tags for a document.
    tags = c.list_tags_on_document(
        "fb444eb8e68437bae06232b9f5091bccff62a768ca09e92eb5c9c2cf9d17c426"
    )
    print(tags)

``add_tag_to_document``
^^^^^^^^^^^^^^^^^^^^^^^

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. code:: python

    from censys.search import CensysHosts

    h = CensysHosts()

    # Add a tag to a document.
    h.add_tag_to_document("123")

``remove_tag_from_document``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Below we show an example using the :attr:`CensysCerts <censys.search.v2.CensysCerts>` index.

.. code:: python

    from censys.search import CensysCerts

    c = CensysCerts()

    # Remove a tag from a document.
    c.remove_tag_from_document(
        "fb444eb8e68437bae06232b9f5091bccff62a768ca09e92eb5c9c2cf9d17c426"
    )

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

**Please note this method is only available only for the CensysHosts index.**

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. code:: python

    from censys.search import CensysHosts

    h = CensysHosts()

    # Fetch a list of hosts with the specified tag.
    hosts = h.list_hosts_with_tag("123")
    print(hosts)
