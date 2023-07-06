Usage v1
========

The Censys Search API provides functionality for interacting with Censys resources such as Data, and for viewing Account information such as query quota.

There is one API options that this library provides access to:

-  :attr:`data <censys.search.v1.CensysData>` - Returns collections of scan series whose metadata includes a description of the data collected in the series and links to the individual scan results.

More details about each option can be found in the `Censys API documentation <https://search.censys.io/api>`__. A list of index fields can be found in the `Censys API definitions page <https://search.censys.io/certificates/help>`__.

.. note::

   Please note that the Censys Search Certificates v1 API is being deprecated. Please use the :ref:`CensysCerts (v2) index <usage-v2:Usage v2>` for this functionality.

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

Below we show an example using the :attr:`CensysHosts <censys.search.v2.CensysHosts>` index.

.. code:: python

    from censys.search import CensysHosts

    c = CensysHosts()

    # Gets account data
    account = c.account()
    print(account)

    # Gets account quota
    quota = c.quota()
    print(quota)
