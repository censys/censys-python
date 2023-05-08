CLI Usage
=========

.. raw:: html
    :file: cli.html

Before continuing please ensure you have successfully configured your credentials.

.. prompt:: bash

    censys config

The configuration file by default is written to ``~/.config/censys/censys.cfg``, but you can change this by setting the ``CENSYS_CONFIG_PATH`` environment variable.

.. prompt:: bash

    export CENSYS_CONFIG_PATH=/path/to/config/file

Optionally, you can enable tab completion for the CLI by adding this line to your `~/.bashrc`, `~/.zshrc`, or equivalent.

.. prompt:: bash

    eval "$(register-python-argcomplete censys)"

.. note::

    Please note that autocomplete is supported for field names in the `search` command.


``search``
----------

Below we show an example of searching hosts from the CLI.

.. prompt:: bash

    censys search 'services.http.response.html_title: "Dashboard"'

By combining the ``search`` command with ``jq`` we can easily manipulate the output to get the desired fields.

.. prompt:: bash

    censys search 'services.service_name: ELASTICSEARCH' | jq -c '.[] | {ip: .ip}'

By setting the ``--pages`` flag to ``-1`` we can get all pages of results.

.. prompt:: bash

    censys search 'ip: 8.8.8.0/16' --pages -1 | jq -c '[.[] | .ip]'

By settings the ``--index-type`` flag we can search other indexes such as ``certificates``.

.. prompt:: bash

    censys search 'parsed.subject_dn: "censys.io"' --index-type certificates

For the ``certificates`` index we can also add the ``--fields`` flag to specify which fields we want returned.

.. prompt:: bash

    censys search 'parsed.subject.country: AU' --index-type certificates --fields parsed.issuer.organization

``view``
--------

Below we show an example of viewing a host from the CLI.

.. prompt:: bash

    censys view 8.8.8.8

Below we show an example of viewing a certificate from the CLI.

.. prompt:: bash

    censys view 9b267decc8d23586dc4c56dd0789574cab0f28581ef354ff2fcec8ca6d992fc2 --index-type certificates

You can save results to a file using the ``-o`` argument.

.. prompt:: bash

    censys view 8.8.8.8 -o google.json

We can then parse this json with something like ``jq``.

.. prompt:: bash

    cat google.json | jq '[.services[] | {port: .port, protocol: .service_name}]'

If you have access to historical ``hosts`` data you can view the data at a specific point in time using the ``--at-time`` argument.

.. prompt:: bash

    censys view 1.1.1.1 --at-time 2023-01-01

.. note::

    The ``--at-time`` argument is only available for the ``hosts`` index.

``subdomains``
--------------

Below we show an example of subdomain enumeration from the CLI.

.. prompt:: bash

    censys subdomains censys.io

You can limit the number of results by setting the ``--max-records`` flag.

.. prompt:: bash

    censys subdomains censys.io --max-records 10

We can then output the results in JSON format using the ``--json`` flag.

.. prompt:: bash

    censys subdomains censys.io --json

``account``
-----------

Below we show an example of viewing your account information from the CLI.

.. prompt:: bash

    censys account

You can also request the JSON version of your account information.

.. prompt:: bash

    censys account --json

``asm``
-------

``add-seeds``
^^^^^^^^^^^^^

Below we show an example of adding seeds from the CLI.

.. prompt:: bash

    censys asm add-seeds -j '["1.1.1.1"]'

You can also add seeds from STDIN using the ``-i -`` argument.
In the example below we are adding IPs from a Censys Search.

.. prompt:: bash

    censys search 'services.tls.certificates.leaf_data.issuer.common_name: "Roomba CA"' | jq '[.[] | .ip]' | censys asm add-seeds -i -

You can also add seeds from a nmap XML file using the ``--nmap-xml`` argument.
In the example below we are adding IPs from a nmap scan on ``censys.io``.

.. prompt:: bash

    nmap censys.io -oX censys.xml
    censys asm add-seeds --nmap-xml censys.xml
