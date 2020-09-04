"""
Interact with the Censys' Data API.

Classes:
    CensysData
"""

from censys.base import CensysAPIBase


class CensysData(CensysAPIBase):

    _PREFIX = "/data"

    def get_series(self):
        return self._get(self._PREFIX)

    def view_series(self, series: str):
        path = "/".join([self._PREFIX, series])
        return self._get(path)

    def view_result(self, series: str, result: str):
        path = "/".join([self._PREFIX, series, result])
        return self._get(path)
