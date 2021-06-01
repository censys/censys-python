ASM Usage
=========

The Censys ASM API provides functionality for interacting with Censys ASM endpoints such as Seeds, Assets, and Logbook Events.

There are three API options that this library provides access to:

-  ``seeds`` - Provides programmatic management of seeds in the ASM platform.
-  ``assets`` - Returns asset data for hosts, certificates, and domains. This option also allows the user to manage tags and comments on assets.
-  ``events`` - Returns logbook events. Can be used to execute targeted searches for events based on start id or date, and event type filters.

More details about each option can be found in the Censys ASM API documentation: https://app.censys.io/api-docs. Users can also test example requests from the API documentation page.

Python class objects can be used individually, but must be initialized for each resource type (Seeds, Assets, and Events).

-  ``Seeds()``
-  ``Assets("ASSET_TYPE ["hosts" | "certificates" | "domains"]", )``
-  ``Events()``

Alternatively, all three class objects can be used together by initializing an AsmClient object. This client wraps the three APIs under one object for ease of use.

-  ``AsmClient()``


``Seeds``
----------

Below we show examples for **listing seeds** from the Censys ASM platform.

.. code:: python3

    from censys.asm import Seeds

    s = Seeds()

    # Get all seeds
    seeds = s.get_seeds()
    print(seeds)

    # Get a specific type of seed. Optional seed types are ["IP_ADDRESS", "DOMAIN_NAME", "CIDR", "ASN"]
    # Here we get IP address seeds.
    seeds = s.get_seeds('IP_ADDRESS')
    print(seeds)

    # Get a single seed by its ID (here we get seed with ID=3)
    seeds = s.get_seeds(3)
    print(seeds)

Below we show examples for **adding seeds** to the Censys ASM platform.

.. code:: python3

    from censys.asm import Seeds

    s = Seeds()

    # Add a list of seeds. To add a single seed, just pass a list containing one seed.
    # Here, we add two ASN seeds.
    seed_list = [
        {"type": "ASN", "value": 99998, "label": "seed-test-label"},
        {"type": "ASN", "value": 99999, "label": "seed-test-label"}
    ]
    s.add_seeds(seed_list)

    # Add a list of seeds, replacing existing seeds with a specified label
    # Here, all seeds with label="seed-test-label" will be removed and then
    # Seeds 99996 and 99997 will be added.
        seed_list = [
        {"type": "ASN", "value": 99996},
        {"type": "ASN", "value": 99997}
    ]
    s.replace_seeds_by_label("seed-test-label", seed_list)

Below we show examples for **deleting seeds** from the Censys ASM platform.


.. code:: python3

    from censys.asm import Seeds

    s = Seeds()

    # Delete all seeds with a specified label
    # Here we delete all seeds with label="seed-test-label"
    s.delete_seeds_by_label("seed-test-label")

    # Delete a seed by its ID
    # Here, a seed with ID=224 will be deleted.
    s.delete_seed_by_id(224)


``Assets``
----------
There are three types of assets (Hosts, Certificates, Domains). Each asset type shares the same API interface so we will use a mixture of asset types in the following examples.

Below we show examples for **viewing assets** on the Censys ASM platform.

.. code:: python

    from censys.asm import HostsAssets

    h = HostsAssets()

    # Get a generator that returns hosts
    hosts = h.get_assets()
    print(next(hosts))

    # Get a single host by ID (here we get host with ID="0.0.0.0")
    host = h.get_asset_by_id("0.0.0.0")
    print(host)

Below we show examples for **managing asset comments** via the ASM API.

.. code:: python

    from censys.asm import DomainsAssets

    d = DomainsAssets()

    # Get a generator that returns all comments on a specific domain asset
    # Here we get all comments on the domain with ID="my_domain.com"
    comments = d.get_comments("my_domain.com")
    print(next(comments))

    # Get a single comment on a specific domain by comment ID
    # Here we look at domain with ID="my_domain.com" and get comment with ID=3
    comment = d.get_comment_by_id("my_domain.com", 3)
    print(comment)

    # Add a comment to a domain asset
    # Here we add comment "hello world" to domain with ID="my_domain.com"
    d.add_comment("my_domain.com", "hello world")

Below we show examples for **managing asset tags** via the ASM API.

.. code:: python

    from censys.asm import CertificatesAssets

    c = CertificatesAssets()
    cert_sha = "0006afc1ddc8431aa57c812adf028ab4f168b25bf5f06e94af86edbafa88dfe0"

    # Add a tag to a certificate asset
    # Here we add tag "New" to certificate with ID=cert_sha
    c.add_tag(cert_sha, "New")

    # We can optionally give the tag a hexadecimal color where the default=#ffffff (white)
    # Here we add a blue tag "New-2" to certificate with ID=cert_sha
    c.add_tag(cert_sha, "New-2", color="#0011ff")

    # Delete a tag by tag name
    # Here we delete tag name="New" from certificate with ID=cert_sha
    c.delete_tag(cert_sha, "New")

``Events``
----------

.. note::

    Note that all timestamp fields in logbook operations use **ISO-8601** format. This is the full list of event types that can be used as filters:

    - ``CERT``
    - ``CERT_RISK``
    - ``DOMAIN``
    - ``DOMAIN_EXPIRATION_DATE``
    - ``DOMAIN_MAIL_EXCHANGE_SERVER``
    - ``DOMAIN_NAME_SERVER``
    - ``DOMAIN_REGISTRAR``
    - ``DOMAIN_RISK``
    - ``DOMAIN_SUBDOMAIN``
    - ``HOST``
    - ``HOST_CERT``
    - ``HOST_PORT``
    - ``HOST_PROTOCOL``
    - ``HOST_RISK``
    - ``HOST_SOFTWARE``
    - ``HOST_VULNERABILITY``

Below we show examples for **creating a logbook cursor** for retrieving filtered events.

.. code:: python

    from censys.asm import Events

    e = Events()

    # Get a logbook cursor beginning at timestamp "2020-04-22T06:55:01.000Z"
    cursor = e.get_cursor("2020-04-22T06:55:01.000Z")
    print(cursor)

    # Get a logbook cursor beginning at event ID=10
    cursor = e.get_cursor(10)
    print(cursor)

    # Get a logbook cursor that filters on events of type "CERT" and "CERT_RISK"
    cursor = e.get_cursor(filters=["CERT", "CERT_RISK"])
    print(cursor)

    # Get a logbook cursor combining previous start ID and filters
    cursor = e.get_cursor(10, filters=["CERT", "CERT_RISK"])
    print(cursor)

Below we show examples for **getting logbook events.**

.. code:: python

    from censys.asm import Events

    e = Events()

    # Get a generator that returns all events
    events = e.get_events()
    print(next(events))

    # Get events based off cursor specifications
    events = e.get_events(cursor)
    print(next(events))

``AsmClient``
-------------

The Censys AsmClient wraps the Seeds, Assets, and Events classes into a single object. It can be used as a single point of interaction for all three APIs.

Below we show how to initialize the AsmClient class object as well as a couple examples of its use. Note that with the AsmClient object, all Seeds, Assets, and Event operations can be accessed in a similar way as the individual APIs above.

.. code:: python

    from censys.asm import AsmClient

    client = AsmClient()

    # Get all seeds
    seeds = client.seeds.get_seeds()
    print(seeds)

    # Get all domain assets
    domains = client.domains.get_assets()
    print(next(domains))

    # Get all events
    events = client.events.get_events()
    print(next(events))

