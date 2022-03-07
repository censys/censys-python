CLI Usage
=========

Before continuing please ensure you have successfully configured your credentials.

.. prompt:: bash

    censys config

The configuration file by default is writen to ``~/.config/censys/censys.cfg``, but you can change this by setting the ``CENSYS_CONFIG_PATH`` environment variable.

.. prompt:: bash

    export CENSYS_CONFIG_PATH=/path/to/config/file


``search``
----------

Below we show an example of Searching from the CLI.

.. prompt:: bash

    censys search 'services.http.response.html_title: "Dashboard"'

By combining the ``search`` command with ``jq`` we can easily manipulate the output to get the desired fields.

.. prompt:: bash

    censys search 'services.service_name: ELASTICSEARCH' | jq -c '.[] | {ip: .ip}'

By setting the ``--pages`` flag to ``-1`` we can get all pages of results.

.. prompt:: bash

    censys search 'ip: 8.8.8.0/16' --pages -1 | jq -c '[.[] | .ip]'

``view``
--------

Below we show an example of Viewing a host from the CLI.

.. prompt:: bash

    censys view 8.8.8.8

You can save results to a file using the ``-o`` argument.

.. prompt:: bash

    censys view 8.8.8.8 -o google.json

We can then parse this json with something like ``jq``.

.. prompt:: bash

    cat google.json | jq '[.services[] | {port: .port, protocol: .service_name}]'

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
