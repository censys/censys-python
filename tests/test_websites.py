import unittest

from utils import required_env

from censys.websites import CensysWebsites


@required_env
class CensysWebsitesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._api = CensysWebsites()

    def testGet(self):
        self._api.view("google.com")

    def testSearch(self):
        list(self._api.search("*", max_records=10))

    def testReport(self):
        self._api.report("*", "80.http.get.headers.server.raw")


if __name__ == "__main__":
    unittest.main()
