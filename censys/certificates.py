"""
Interact with the Censys' Certificate API.

Classes:
    CensysCertificates
"""

from typing import List

from censys.base import CensysIndex


class CensysCertificates(CensysIndex):

    INDEX_NAME = "certificates"
    MAX_PER_BULK_REQUEST = 50

    def __init__(self, *args, **kwargs):
        CensysIndex.__init__(self, *args, **kwargs)
        self.bulk_path = "/bulk/{}".format(self.INDEX_NAME)

    def bulk(self, fingerprints: List[str]) -> dict:
        result = dict()
        start = 0
        end = self.MAX_PER_BULK_REQUEST
        while start < len(fingerprints):
            data = {"fingerprints": fingerprints[start:end]}
            result.update(self._post(self.bulk_path, data=data))
            start = end
            end += self.MAX_PER_BULK_REQUEST

        return result
