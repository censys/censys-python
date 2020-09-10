import unittest

from utils import CensysTestCase

from censys.websites import CensysWebsites


class CensysWebsitesTests(CensysTestCase):

    MAX_RECORDS = 10
    EXPECTED_REPORT_FIELDS = {"metadata", "results", "status"}

    @classmethod
    def setUpClass(cls):
        cls._api = CensysWebsites()

    def test_view(self):
        res = self._api.view("google.com")
        self.assertIsInstance(res, dict)

    def test_search(self):
        res = list(self._api.search("*", max_records=self.MAX_RECORDS))
        self.assertLessEqual(len(res), self.MAX_RECORDS)

    def test_report(self):
        res = self._api.report("*", "80.http.get.headers.server.raw")
        self.assertSetEqual(set(res.keys()), self.EXPECTED_REPORT_FIELDS)


if __name__ == "__main__":
    unittest.main()
