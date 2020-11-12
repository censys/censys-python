"""
Interact with the Censys Search Website API.
"""

from censys.api import CensysSearchAPI


class CensysWebsites(CensysSearchAPI):
    """
    Interacts with the IPv4 index.
    """

    INDEX_NAME = "websites"
    """Name of Censys Index."""
