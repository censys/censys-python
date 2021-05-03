Advanced Usage
==============

Proxies
-------

If you need to use a proxy, you can configure resource indexes with the proxies argument:

.. code:: python

    from censys.search import CensysIPv4

    proxies = {
        "https": "http://10.10.1.10:1080",
    }

    c = CensysIPv4(proxies=proxies)

    for page in c.search(
        "443.https.get.headers.server: Apache AND location.country: Japan", max_records=10
    ):
        print(page)

.. note::

   HTTP proxies will be ignored in favor of HTTPS proxies.

See Requests :ref:`requests:proxies` for more information on the format of proxies.
