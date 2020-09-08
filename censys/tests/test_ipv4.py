import unittest

from utils import CensysTestCase

from censys.exceptions import CensysAPIException
from censys.ipv4 import CensysIPv4


class CensysIPv4Tests(CensysTestCase):

    SAMPLE_IPV4 = "8.8.8.8"
    MAX_RECORDS = 10
    EXPECTED_METADATA_KEYS = {"backend_time", "count", "page", "pages", "query"}
    EXPECTED_SEARCH_KEYS = {"ip", "location", "protocols"}
    EXCEPTED_SEARCH_FIELDS = {"ip", "updated_at"}
    EXCEPTED_REPORT_FIELDS = {"metadata", "results", "status"}

    @classmethod
    def setUpClass(cls):
        cls._api = CensysIPv4()

    def test_metadata(self):
        res = self._api.metadata(self.SAMPLE_IPV4)
        self.assertSetEqual(set(res.keys()), self.EXPECTED_METADATA_KEYS)
        self.assertEqual(res.get("page"), 1)
        self.assertEqual(res.get("query"), self.SAMPLE_IPV4)

    def test_view(self):
        res = self._api.view(self.SAMPLE_IPV4)
        self.assertIn("ip", res)
        self.assertIn("updated_at", res)
        self.assertIn("location", res)
        self.assertIn("autonomous_system", res)

    def test_search(self):
        res = list(
            self._api.search("*", max_records=self.MAX_RECORDS, flatten=False)
        )
        self.assertLessEqual(len(res), self.MAX_RECORDS)
        self.assertSetEqual(set(res[0].keys()), self.EXPECTED_SEARCH_KEYS)

    def test_search_fields(self):
        res = list(
            self._api.search(
                "*",
                fields=list(self.EXCEPTED_SEARCH_FIELDS),
                max_records=self.MAX_RECORDS,
                flatten=False,
            )
        )
        self.assertLessEqual(len(res), self.MAX_RECORDS)
        self.assertSetEqual(set(res[0].keys()), self.EXCEPTED_SEARCH_FIELDS)

    def test_search_explicit_page(self):
        res = list(self._api.search("*", page=3, max_records=self.MAX_RECORDS))
        self.assertLessEqual(len(res), self.MAX_RECORDS)

    def test_empty_search(self):
        with self.assertRaises(CensysAPIException):
            self._api._post("search/ipv4", data={"query1": "query"})

    def test_beyond_max_pages(self):
        with self.assertRaises(CensysAPIException):
            list(self._api.search("*", page=250))

    def test_bad_page_search(self):
        with self.assertRaises(Exception):
            list(self._api.search("*", page="x", max_records=self.MAX_RECORDS))

    def test_bad_fields_search(self):
        with self.assertRaises(CensysAPIException):
            list(self._api.search("*", fields="test", max_records=self.MAX_RECORDS))

    def test_report(self):
        bucket_count = 100
        res = self._api.report(
            "80.http.get.headers.server: Apache", "location.country", bucket_count
        )
        self.assertSetEqual(set(res.keys()), self.EXCEPTED_REPORT_FIELDS)
        self.assertEqual(len(res["results"]), bucket_count)


if __name__ == "__main__":
    unittest.main()
