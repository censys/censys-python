"""
Interact with the Censys Website API.
"""

from censys.base import CensysIndex


class CensysWebsites(CensysIndex):
    """
    Interacts with the IPv4 index.
    """

    INDEX_NAME = "websites"
    """Name of Censys Index."""
