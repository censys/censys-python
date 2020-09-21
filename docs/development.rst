Development 
===========

Clone the repository:

.. tabs::

   .. tab:: with SSH

      .. prompt:: bash $

        git clone git@github.com:censys/censys-python.git

   .. tab:: with HTTPS

      .. prompt:: bash $
      
        git clone https://github.com/censys/censys-python.git

Install dependencies via ``pip``:

.. tabs::

   .. tab:: with macOS

      .. prompt:: bash $

        pip install -e ".[dev]"

   .. tab:: with Linux

      .. prompt:: bash $
      
        pip install -e .[dev]

Run the test suite with ``pytest``. More information about testing is available at :ref:`testing:Testing`.
