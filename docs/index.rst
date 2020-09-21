.. Censys Python documentation master file, created by
   sphinx-quickstart on Fri Sep 11 10:57:18 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Censys Python's documentation!
-----------------------------------------

.. automodule:: censys
   :members:

Quick start
-----------

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


.. toctree::
   :maxdepth: 1
   :caption: Table of Contents

   usage
   cli
   censys
   development
   testing
   contributing
