"""
Interact with the Censys' IPv4 API.

Classes:
    CensysIPv4
"""

from censys.base import CensysIndex


class CensysIPv4(CensysIndex):

    INDEX_NAME = "ipv4"
