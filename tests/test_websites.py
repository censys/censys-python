import unittest

from utils import CensysTestCase

from censys.websites import CensysWebsites


class CensysWebsitesTests(CensysTestCase):

    MAX_RECORDS = 10
    EXCEPTED_REPORT_FIELDS = {"metadata", "results", "status"}

    @classmethod
    def setUpClass(cls):
        cls._api = CensysWebsites()

    def test_view(self):
        response = self._api.view("google.com")
        self.assertIsInstance(response, dict)

    def test_search(self):
        response = list(self._api.search("*", max_records=self.MAX_RECORDS))
        self.assertLessEqual(len(response), self.MAX_RECORDS)

    def test_report(self):
        response = self._api.report("*", "80.http.get.headers.server.raw")
        self.assertSetEqual(set(response.keys()), self.EXCEPTED_REPORT_FIELDS)


if __name__ == "__main__":
    unittest.main()
