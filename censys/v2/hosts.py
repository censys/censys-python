"""Interact with the Censys Search Host API."""
from .api import CensysSearchAPIv2


class CensysHosts(CensysSearchAPIv2):
    """Interacts with the Hosts index."""

    INDEX_NAME = "hosts"
    """Name of Censys Index."""
