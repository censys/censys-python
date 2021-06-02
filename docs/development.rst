Development 
===========

Clone the repository:

.. tabs::

   .. tab:: SSH

      .. prompt:: bash $

        git clone git@github.com:censys/censys-python.git

   .. tab:: HTTPS

      .. prompt:: bash $
      
        git clone https://github.com/censys/censys-python.git
   
   .. tab:: GitHub CLI

      .. prompt:: bash $
      
        gh repo clone censys/censys-python

Install dependencies via ``pip``:

.. prompt:: bash $

   cd censys-python/
   pip install -e ".[dev]"

Run the test suite with ``pytest``. More information about testing is available at :ref:`testing:Testing`.
