import unittest

from utils import required_env

from censys.base import CensysException
from censys.ipv4 import CensysIPv4


@required_env
class CensysIPv4Tests(unittest.TestCase):

    MAX_RECORDS = 10
    EXPECTED_SEARCH_KEYS = {"ip", "location", "protocols"}
    EXCEPTED_SEARCH_FIELDS = {"ip", "updated_at"}
    EXCEPTED_REPORT_FIELDS = {"metadata", "results", "status"}

    @classmethod
    def setUpClass(cls):
        cls._api = CensysIPv4()

    def test_view(self):
        # hopefully will always be found
        response = self._api.view("8.8.8.8")
        self.assertIn("ip", response)
        self.assertIn("updated_at", response)
        self.assertIn("location", response)
        self.assertIn("autonomous_system", response)

    def test_search(self):
        response = list(
            self._api.search("*", max_records=self.MAX_RECORDS, flatten=False)
        )
        self.assertLessEqual(len(response), self.MAX_RECORDS)
        self.assertSetEqual(set(response[0].keys()), self.EXPECTED_SEARCH_KEYS)

    def test_search_fields(self):
        response = list(
            self._api.search(
                "*",
                fields=list(self.EXCEPTED_SEARCH_FIELDS),
                max_records=self.MAX_RECORDS,
                flatten=False,
            )
        )
        self.assertLessEqual(len(response), self.MAX_RECORDS)
        self.assertSetEqual(set(response[0].keys()), self.EXCEPTED_SEARCH_FIELDS)

    def test_search_explicit_page(self):
        response = list(self._api.search("*", page=3, max_records=self.MAX_RECORDS))
        self.assertLessEqual(len(response), self.MAX_RECORDS)

    def test_empty_search(self):
        with self.assertRaises(CensysException):
            self._api._post("search/ipv4", data={"query1": "query"})

    def test_beyond_max_pages(self):
        with self.assertRaises(CensysException):
            list(self._api.search("*", page=250))

    def test_bad_page_search(self):
        with self.assertRaises(Exception):
            list(self._api.search("*", page="x", max_records=self.MAX_RECORDS))

    def test_bad_fields_search(self):
        with self.assertRaises(CensysException):
            list(self._api.search("*", fields="test", max_records=self.MAX_RECORDS))

    def test_report(self):
        bucket_count = 100
        response = self._api.report(
            "80.http.get.headers.server: Apache", "location.country", bucket_count
        )
        self.assertSetEqual(set(response.keys()), self.EXCEPTED_REPORT_FIELDS)
        self.assertEqual(len(response["results"]), bucket_count)


if __name__ == "__main__":
    unittest.main()
