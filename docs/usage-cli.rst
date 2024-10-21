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

See CLI command :ref:`asm add-seeds<cli:censys asm add-seeds>` for detail documentation of parameters.

Below we show an example of adding seeds from the CLI.

.. prompt:: bash

    censys asm add-seeds -j '["1.1.1.1"]'

You can add seeds from JSON or CSV files. JSON is assumed unless ``--csv`` is specified.
The CSV file option is shown here.

.. prompt:: bash

    censys asm add-seeds --csv -i 'good_seeds.csv'

.. list-table:: CSV File Format
   :header-rows: 1

   * - type
     - value
     - label
   * - IP_ADDRESS
     - 1.1.1.1
     - Example Label
   * - DOMAIN_NAME
     - one.one.one.one
     - Example Label

You can also add seeds from STDIN using the ``-i -`` argument.
In the example below we are adding IPs from a Censys Search.

.. prompt:: bash

    censys search 'services.tls.certificates.leaf_data.issuer.common_name: "Roomba CA"' | jq '[.[] | .ip]' | censys asm add-seeds -i -

You can also add seeds from an nmap XML file using the ``--nmap-xml`` argument.
In the example below we are adding IPs from a nmap scan on ``censys.io``.

.. prompt:: bash

    nmap censys.io -oX censys.xml
    censys asm add-seeds --nmap-xml censys.xml

``delete-seeds``
^^^^^^^^^^^^^^^^

See CLI command :ref:`asm delete-seeds<cli:censys asm delete-seeds>` for detail documentation of parameters.

Below we show an example of deleting seeds from the CLI.

.. prompt:: bash

    censys asm delete-seeds -j '["1.1.1.1"]'

You can delete seeds using file input as well, including CSV files.

.. prompt:: bash

    censys asm delete-seeds --csv -i 'bad_seeds.csv'

.. list-table:: CSV File Format
   :header-rows: 1

   * - id
     - type
     - value
     - label
   * - 1
     - IP_ADDRESS
     - 1.1.1.1
     - Example Label
   * - 2
     - DOMAIN_NAME
     - one.one.one.one
     - Example Label

``delete-all-seeds``
^^^^^^^^^^^^^^^^^^^^

See CLI command :ref:`asm delete-all-seeds<cli:censys asm delete-all-seeds>` for detail documentation of parameters.

Below we show an example of deleting all seeds from the CLI.  You will be prompted to confirm.

.. prompt:: bash

    censys asm delete-all-seeds

If you want to delete all seeds without a prompt, you can use the ``--force`` parameter.

.. prompt:: bash

    censys asm delete-all-seeds --force


``delete-labeled-seeds``
^^^^^^^^^^^^^^^^^^^^^^^^

See CLI command :ref:`asm delete-labeled-seeds<cli:censys asm delete-labeled-seeds>` for detail documentation of parameters.

Below we show an example of deleting all seeds with a given label from the CLI.

.. prompt:: bash

    censys asm delete-labeled-seeds -l "Some Label"

``replace-labeled-seeds``
^^^^^^^^^^^^^^^^^^^^^^^^^

See CLI command :ref:`asm replace-labeled-seeds<cli:censys asm replace-labeled-seeds>` for detail documentation of parameters.

Below we show an example of replacing labeled seeds from the CLI, which will replace all existing seeds that have
the specified label with the provided seeds, which will also have that label applied.

.. prompt:: bash

    censys asm replace-labeled-seeds -l "Some Label" -j '["1.1.1.1"]'

You can also use a variety of methods to specific the new seeds, including providing them in a CSV file.

.. prompt:: bash

    censys asm replace-labeled-seeds -l "Some Label" --csv -i 'new_seeds.csv'

``list-seeds``
^^^^^^^^^^^^^^

See CLI command :ref:`asm list-seeds<cli:censys asm list-seeds>` for detail documentation of parameters.

Below we show an example of listing all seeds in CSV file format and appending it to a file.

.. prompt:: bash

    censys asm list-seeds --csv >> seeds.csv

You can also filter the seeds by type (``-t``) and/or label (``-l``).

.. prompt:: bash

    censys asm list-seeds -t 'IP_ADDRESS' -l 'Some Label' >> filtered_seeds.json


``list-saved-queries``
^^^^^^^^^^^^^^^^^^^^^^

See CLI command :ref:`asm list-saved-queries<cli:censys asm list-saved-queries>` for detail documentation of parameters.

Below we show an example of listing all saved queries in CSV file format and appending it to a file.

.. prompt:: bash

    censys asm list-saved-queries --csv >> saved_queries.csv

You can also filter the saved queries by query name prefix (``--query-name-prefix``) and/or filter term (``--filter-term``).

.. prompt:: bash

    censys asm list-saved-queries --query-name-prefix 'Some Prefix' --filter-term 'Some Term' >> filtered_saved_queries.json


``add-saved-query``
^^^^^^^^^^^^^^^^^^^

See CLI command :ref:`asm add-saved-query<cli:censys asm add-saved-query>` for detail documentation of parameters.

Below we show an example of adding a saved query from the CLI.

.. prompt:: bash

    censys asm add-saved-query --query-name 'Some Query' --query 'services.http.response.html_title: "Dashboard"'

``get-saved-query-by-id``
^^^^^^^^^^^^^^^^^^^^^^^^^

See CLI command :ref:`asm get-saved-query-by-id<cli:censys asm get-saved-query-by-id>` for detail documentation of parameters.

Below we show an example of getting a saved query by ID from the CLI.

.. prompt:: bash

    censys asm get-saved-query-by-id --query-id 'Some ID'

``edit-saved-query-by-id``
^^^^^^^^^^^^^^^^^^^^^^^^^^

See CLI command :ref:`asm edit-saved-query-by-id<cli:censys asm edit-saved-query-by-id>` for detail documentation of parameters.

Below we show an example of editing a saved query by ID from the CLI.

.. prompt:: bash

    censys asm edit-saved-query-by-id --query-id 'Some ID' --query-name 'Some Query' --query 'services.http.response.html_title: "Dashboard"'

``delete-saved-query-by-id``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See CLI command :ref:`asm delete-saved-query-by-id<cli:censys asm delete-saved-query-by-id>` for detail documentation of parameters.

Below we show an example of deleting a saved query by ID from the CLI.

.. prompt:: bash

    censys asm delete-saved-query-by-id --query-id 'Some ID'

``execute-saved-query-by-name``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See CLI command :ref:`asm execute-saved-query-by-name<cli:censys asm execute-saved-query-by-name>` for detail documentation of parameters.

Below we show an example of executing a saved query by name from the CLI.

.. prompt:: bash

    censys asm execute-saved-query-by-name --query-name 'Some query name'

``execute-saved-query-by-id``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See CLI command :ref:`asm execute-saved-query-by-id<cli:censys asm execute-saved-query-by-id>` for detail documentation of parameters.

Below we show an example of executing a saved query by ID from the CLI.

.. prompt:: bash

    censys asm execute-saved-query-by-id --query-id 'Some query ID'

``search``
^^^^^^^^^^

See CLI command :ref:`asm search<cli:censys asm search>` for detail documentation of parameters.

Below we show an example of executing an inventory search query from the CLI.

.. prompt:: bash

    censys asm search --query 'Some query'
