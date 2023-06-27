ASM Usage
=========

The Censys ASM API provides functionality for interacting with Censys ASM endpoints such as Seeds, Assets, Logbook Events, Risks, and Inventory Search.

The following API clients provided are:

-  :attr:`seeds <censys.asm.Seeds>` - Provides programmatic management of seeds in the ASM platform.
-  :attr:`assets <censys.asm.Assets>` - Returns asset data for hosts, certificates, and domains. This option also allows the user to manage tags and comments on assets.
-  :attr:`logbook <censys.asm.logbook.Logbook>` - Returns logbook events. Can be used to execute targeted searches for events based on start id or date, and event type filters.
-  :attr:`risks <censys.asm.risks.Risks>` - Returns risk data for hosts, certificates, and domains. This option also allows the user to get more information about a specific risk.
-  :attr:`inventory <censys.asm.inventory.InventorySearch>` - Returns inventory data for hosts, certificates, and domains. This option also allows the user to Search for assets based on a variety of criteria.
-  :attr:`web entities <censys.asm.assets.web_entities.WebEntitiesAssets>` - Returns web entities instances. This option also allows the user to manage tags and comments on web entities.

More details about each option can be found in the `Censys ASM API documentation <https://app.censys.io/api-docs>`__. Users can also test example requests from the API documentation page.

Python class objects can be used individually, but must be initialized for each resource type (Seeds, Assets, Events, Risks, Inventory, Clouds).

-  :attr:`Seeds <censys.asm.Seeds>`
-  :attr:`Assets <censys.asm.Assets>`

   -  :attr:`CertificatesAssets <censys.asm.CertificatesAssets>`
   -  :attr:`DomainsAssets <censys.asm.DomainsAssets>`
   -  :attr:`HostsAssets <censys.asm.HostsAssets>`
   -  :attr:`ObjectStoragesAssets <censys.asm.ObjectStoragesAssets>`
   -  :attr:`SubdomainsAssets <censys.asm.SubdomainsAssets>`
   -  :attr:`WebEntitiesAssets <censys.asm.WebEntitiesAssets>`

-  :attr:`Logbook <censys.asm.logbook.Logbook>`
-  :attr:`Risks <censys.asm.risks.Risks>`
-  :attr:`InventorySearch <censys.asm.inventory.InventorySearch>`

Alternatively, all three class objects can be used together by initializing an AsmClient object. This client wraps the three APIs under one object for ease of use.

-  :attr:`AsmClient <censys.asm.AsmClient>`


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
    seeds = s.get_seeds("IP_ADDRESS")
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
        {"type": "ASN", "value": 99999, "label": "seed-test-label"},
    ]
    s.add_seeds(seed_list)

    # Add a list of seeds, replacing existing seeds with a specified label
    # Here, all seeds with label="seed-test-label" will be removed and then
    # Seeds 99996 and 99997 will be added.
    seed_list = [{"type": "ASN", "value": 99996}, {"type": "ASN", "value": 99997}]
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
There are four types of assets (Hosts, Certificates, Domains, and Subdomains). Each asset type shares the same API interface so we will use a mixture of asset types in the following examples.

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

Below we show examples for **subdomain asset tags** via the ASM API.

.. code:: python

    from censys.asm import AsmClient

    client = AsmClient()

    sub = client.get_subdomains("my_domain.com")

    # Add a tag to a subdomain under my_domain.com
    sub.add_tag("sub.my_domain.com", "New")

``Logbook``
-----------

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

    from censys.asm import Logbook

    l = Logbook()

    # Get a logbook cursor beginning at timestamp "2020-04-22T06:55:01.000Z"
    cursor = l.get_cursor("2020-04-22T06:55:01.000Z")
    print(cursor)

    # Get a logbook cursor beginning at event ID=10
    cursor = l.get_cursor(10)
    print(cursor)

    # Get a logbook cursor that filters on events of type "CERT" and "CERT_RISK"
    cursor = l.get_cursor(filters=["CERT", "CERT_RISK"])
    print(cursor)

    # Get a logbook cursor combining previous start ID and filters
    cursor = l.get_cursor(10, filters=["CERT", "CERT_RISK"])
    print(cursor)

Below we show examples for **getting logbook events.**

.. code:: python

    from censys.asm import Logbook

    l = Logbook()

    # Get a generator that returns all events
    events = l.get_events()
    print(next(events))

    # Get events based off cursor specifications
    events = l.get_events(cursor)
    print(next(events))

``Risks``
---------

Below we show an example of **getting risk instances**.

.. code:: python

    from censys.asm import Risks

    r = Risks()

    # Get a dict that returns all risk instances
    risk_instances = r.get_risk_instances()
    print(risk_instances)

    # Get a single risk instance by ID
    risk_instance = r.get_risk_instance(1)
    print(risk_instance)

    # Get risk types
    risk_types = r.get_risk_types()
    print(risk_types)

    # Get a single risk type by ID
    risk_type = r.get_risk_type("missing-common-security-headers")
    print(risk_type)

``InventorySearch``
-------------------

Below we show an example of **searching for assets**.

.. code:: python

    from censys.asm import InventorySearch

    i = InventorySearch()

    # Get a dict that contains a list of hits for a search query with pagination
    assets = i.search(workspaces=["my_workspace"], query="host.services.http.response.body: /.*test.*/")
    print(assets)

    # Aggregate search results by a field
    aggregation = i.aggregate(workspaces=["my_workspace"], query="host.services.http.response.body: /.*test.*/")
    print(aggregation)

    # Get list of all available fields
    fields = i.fields()
    print(fields)


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

    # Get all logbook events
    logbook_events = client.logbook.get_events()
    print(next(logbook_events))


``Exceptions``
--------------

.. TODO: Add exceptions
