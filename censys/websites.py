"""
Interact with the Censys' IPv4 API.

Classes:
    CensysWebsites
"""

from censys.base import CensysIndex


class CensysWebsites(CensysIndex):

    INDEX_NAME = "websites"
