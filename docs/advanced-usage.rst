Advanced Usage
==============

Proxies
-------

If you need to use a proxy, you can configure resource indexes with the proxies argument:

.. code:: python

    import censys.ipv4

    proxies = {
            "http": "http://10.10.1.10:3128",
            "https": "http://10.10.1.10:1080",
        }

    c = censys.ipv4.CensysIPv4(proxies=proxies)

    for page in c.search(
        "443.https.get.headers.server: Apache AND location.country: Japan", 
        max_records=10
    ):
        print(page)

See :ref:`requests:proxies` for more information on the format of proxies.
