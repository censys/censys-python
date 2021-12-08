Advanced Usage
==============

Proxies
-------

If you need to use a proxy, you can configure resource indexes with the proxies argument:

.. code:: python

    from censys.search import CensysHosts

    proxies = {
        "https": "http://10.10.1.10:1080",
    }

    c = CensysHosts(proxies=proxies)

    c.account()

.. note::

   HTTP proxies will be ignored in favor of HTTPS proxies.

See Requests :ref:`requests:proxies` for more information on the format of proxies.
