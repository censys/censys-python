Quick Start
===========

Assuming you have Python already, install the package:

.. prompt:: bash

   pip install censys


If you do not have pip installed, get it `here <https://pip.pypa.io/en/stable/installation/>`_.

Configure your credentials:

.. tabs::

   .. tab:: Search API

      .. prompt:: bash

         censys config

      Or you can set the environment variables:

      .. prompt:: bash

         export CENSYS_API_ID=<your-api-id>
         export CENSYS_API_SECRET=<your-api-secret>

      Find your credentials on the `Account page <https://search.censys.io/account/api>`_.

   .. tab:: ASM API

      .. prompt:: bash

         censys asm config

      Or you can set the environment variables:

      .. prompt:: bash

         export CENSYS_ASM_API_KEY=<your-api-key>

      Find your credentials on the `Integrations page <https://app.censys.io/integrations>`_.

Optionally, you can enable tab completion for the CLI by adding this line to your `~/.bashrc`, `~/.zshrc`, or equivalent.

.. prompt:: bash

   eval "$(register-python-argcomplete censys)"

.. note::

   Please note that quotes are required for autocompletion of field names in the `search` command.
