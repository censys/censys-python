"""Interact with the Censys Search IPv4 API."""
from .api import CensysSearchAPIv1


class CensysIPv4(CensysSearchAPIv1):
    """Interacts with the IPv4 index."""

    INDEX_NAME = "ipv4"
    """Name of Censys Index."""
