"""Interact with the Censys Search Website API."""
from .api import CensysSearchAPIv1


class CensysWebsites(CensysSearchAPIv1):
    """Interacts with the Websites index."""

    INDEX_NAME = "websites"
    """Name of Censys Index."""
