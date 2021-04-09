import unittest

import pytest

from ..utils import CensysTestCase

from censys.exceptions import CensysException, CensysSearchException
from censys.v1.ipv4 import CensysIPv4


class CensysIPv4Tests(CensysTestCase):

    SAMPLE_IPV4 = "8.8.8.8"
    MAX_RECORDS = 10
    EXPECTED_METADATA_KEYS = {"backend_time", "count", "page", "pages", "query"}
    EXPECTED_SEARCH_KEYS = {"ip", "location", "protocols"}
    EXPECTED_SEARCH_FIELDS = {"ip", "updated_at"}
    EXPECTED_REPORT_FIELDS = {"metadata", "results", "status"}

    @classmethod
    def setUpClass(cls):
        cls._api = CensysIPv4()

    def test_metadata(self):
        res = self._api.metadata(self.SAMPLE_IPV4)

        assert set(res.keys()) == self.EXPECTED_METADATA_KEYS
        assert res.get("page") == 1
        assert res.get("query") == self.SAMPLE_IPV4

    def test_view(self):
        res = self._api.view(self.SAMPLE_IPV4)

        assert "ip" in res
        assert "updated_at" in res
        assert "location" in res
        assert "autonomous_system" in res

    def test_search(self):
        res = list(self._api.search("*", max_records=self.MAX_RECORDS, flatten=False))

        assert len(res) <= self.MAX_RECORDS
        assert set(res[0].keys()) == self.EXPECTED_SEARCH_KEYS

    def test_search_fields(self):
        res = list(
            self._api.search(
                "*",
                fields=list(self.EXPECTED_SEARCH_FIELDS),
                max_records=self.MAX_RECORDS,
                flatten=False,
            )
        )

        assert len(res) <= self.MAX_RECORDS
        assert set(res[0].keys()) == self.EXPECTED_SEARCH_FIELDS

    def test_search_explicit_page(self):
        res = list(self._api.search("*", page=3, max_records=self.MAX_RECORDS))

        assert len(res) <= self.MAX_RECORDS

    def test_empty_search(self):
        with pytest.raises(CensysSearchException):
            self._api._post("search/ipv4", data={"query1": "query"})

    def test_beyond_max_pages(self):
        with pytest.raises(CensysSearchException):
            list(self._api.search("*", page=250))

    def test_bad_page_search(self):
        with pytest.raises(CensysException, match="Invalid page value: x"):
            list(self._api.search("*", page="x", max_records=self.MAX_RECORDS))

    def test_bad_fields_search(self):
        with pytest.raises(CensysSearchException):
            list(self._api.search("*", fields="test", max_records=self.MAX_RECORDS))

    def test_report(self):
        bucket_count = 100
        res = self._api.report(
            "80.http.get.headers.server: Apache", "location.country", bucket_count
        )

        assert set(res.keys()) == self.EXPECTED_REPORT_FIELDS
        assert len(res["results"]) == bucket_count


if __name__ == "__main__":
    unittest.main()
