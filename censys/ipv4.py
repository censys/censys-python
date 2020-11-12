"""
Interact with the Censys Search IPv4 API.
"""

from censys.api import CensysSearchAPI


class CensysIPv4(CensysSearchAPI):
    """
    Interacts with the IPv4 index.
    """

    INDEX_NAME = "ipv4"
    """Name of Censys Index."""
