Usage Platform
==============

The Censys Platform API provides functionality for interacting with all Censys Platform resources through a unified client interface.

The ``CensysPlatformClient`` class
----------------------------------

The Censys Platform API provides a unified client to access all Censys Platform resources through a single interface.

.. code-block:: python

    from censys.platform import CensysPlatformClient

    # Initialize the client with your credentials
    client = CensysPlatformClient(
        token="YOUR_API_TOKEN",
        organization_id="YOUR_ORGANIZATION_ID"
    )

    # Access different APIs through the client
    hosts = client.hosts                # CensysHosts instance
    certificates = client.certificates  # CensysCertificates instance
    webproperties = client.webproperties  # CensysWebProperties instance
    search = client.search              # CensysSearch instance

Configuration
------------

The Platform API requires specific configuration that is separate from the legacy Censys API configuration. You'll need both a Platform Token and an Organization ID to use the Platform API.

You can configure these credentials in one of the following ways:

1. Using the dedicated platform configuration command:

   .. code-block:: sh

       $ censys platform config

       Censys Platform Token: XXX
       Censys Organization ID: XXX
       Do you want color output? [y/n]: y

   Note that this is different from the legacy ``censys config`` command, which configures only the Search API credentials.

2. Setting environment variables:

   .. code-block:: sh

       # Set these environment variables
       export CENSYS_PLATFORM_TOKEN="your_platform_token"
       export CENSYS_ORGANIZATION_ID="your_organization_id"

3. Passing credentials directly to the client constructor:

   .. code-block:: python

       client = CensysPlatformClient(
           token="your_platform_token",
           organization_id="your_organization_id"
       )

Note that the Platform API configuration is different from the legacy Censys API configuration, which uses API ID and API Secret instead of a Platform Token.

Search API (Unified Search)
--------------------------

The Platform API provides a unified search interface through the `CensysSearch` client. This allows you to search across hosts, certificates, and web properties using the same Censys Query Language (CenQL) syntax.

.. code-block:: python

    # Search for hosts with specific services
    search_query = "host.services: (port = 443 and protocol = 'TCP')"
    search_results = client.search.query(search_query, per_page=10)

    # Check results
    total_results = search_results.get("result", {}).get("total", 0)
    hits = search_results.get("result", {}).get("hits", [])

    # Process results
    for hit in hits:
        print(f"IP: {hit.get('ip')}")

Aggregate data across resources:

.. code-block:: python

    # Aggregate data about services on port 443
    agg_query = "host.services.port: 443"
    agg_field = "host.services.service_name"
    agg_results = client.search.aggregate(agg_query, agg_field)

    # Process aggregation buckets
    buckets = agg_results.get("result", {}).get("buckets", [])
    for bucket in buckets[:5]:
        print(f"{bucket.get('key')}: {bucket.get('count')} hosts")

Hosts API
---------

Access host-specific operations through the ``hosts`` client:

.. code-block:: python

    # View details of a specific host
    host_ip = "8.8.8.8"
    host_details = client.hosts.view(host_ip)

    # Get services running on the host
    services = host_details.get("host", {}).get("services", [])
    for service in services:
        print(f"Port {service.get('port')}: {service.get('service_name')}")

    # Get multiple hosts at once
    host_ips = ["8.8.8.8", "1.1.1.1"]
    bulk_results = client.hosts.bulk_view(host_ips)

    # Get host timeline
    timeline = client.hosts.timeline("8.8.8.8")

Certificates API
---------------

Access certificate-specific operations through the ``certificates`` client:

.. code-block:: python

    # View details of a specific certificate
    cert_id = "fb444eb8e68437bae06232b9f5091bccff62a768ca09e92eb5c9c2cf9d17c426"
    cert_details = client.certificates.view(cert_id)

    # Get certificate fields
    subject = cert_details.get("certificate", {}).get("subject", {})
    issuer = cert_details.get("certificate", {}).get("issuer", {})

    print(f"Subject: {subject.get('common_name')}")
    print(f"Issuer: {issuer.get('common_name')}")

Web Properties API
-----------------

Access web property-specific operations through the ``webproperties`` client:

.. code-block:: python

    # View details of a specific web property
    webprop_id = "example.com:443"
    webprop_details = client.webproperties.view(webprop_id)

    # Get web property information
    name = webprop_details.get("webproperty", {}).get("name")
    protocol = webprop_details.get("webproperty", {}).get("protocol")

    print(f"Name: {name}")
    print(f"Protocol: {protocol}")

Censys Query Language (CenQL)
----------------------------

The Platform API uses the Censys Query Language (CenQL) for searches. CenQL provides a unified syntax for searching across all Censys data types. Key features include:

- Field queries: ``field_name: value`` (case-insensitive substring match)
- Exact equality: ``field_name = value`` (case-sensitive exact match)
- Regex matching: ``field_name =~ pattern``
- Comparison operators: ``field_name > value``, ``field_name < value``
- Nested field queries: ``parent_field: (child_field = value and another_field: value)``

Examples:

.. code-block:: python

    # Hosts with SSH running on port 22
    query1 = "host.services: (port = 22 and protocol = 'SSH')"

    # Hosts with a specific software version
    query2 = "host.services.software: (product = 'httpd' and version = '2.4.62')"

    # Hosts with a specific HTTP header
    query3 = "host.services.endpoints.http.headers: (key = 'Server' and value.headers = 'nginx')"

    # Hosts running nginx with a specific welcome page
    query4 = "host.services: (software.product = 'nginx' and endpoints.http.html_title = 'Welcome to nginx!')"

For more details on CenQL syntax, see the `Censys Query Language documentation <https://docs.censys.com/docs/censys-query-language>`_.

Complete Example
--------------

.. include:: ../examples/platform/platform_client.py
   :literal:
