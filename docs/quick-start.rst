Quick Start 
===========

Assuming you have Python already, install the package:

.. tabs::

   .. tab:: from PyPi

      .. prompt:: bash

         pip install censys

   .. tab:: from GitHub

      .. prompt:: bash

         pip install git+https://github.com/censys/censys-python@master

Configure your credentials:

.. tabs::

   .. tab:: with CLI

      .. prompt:: bash

         censys config

   .. tab:: with environment variables

      .. prompt:: bash
      
         export CENSYS_API_ID="XXX"
         export CENSYS_API_SECRET="XXX"