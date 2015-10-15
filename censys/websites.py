import unittest
from censys import *

class CensysWebsites(CensysAPIBase):

    def search(self, query, page=1, fields=[]):
        data = {
            "query":query,
            "page":page,
            "fields":fields
        }
        return self._post("search/websites", data=data)

    def view(self, domain):
        return self._get("/".join(("view", "websites", domain)))

    def report(self, query, field, buckets):
        pass


class CensysWebsitesTests(unittest.TestCase):

    def setUp(self):
        self._api = CensysWebsites()

    def testGet(self):
        print self._api.view("google.com")

    def testSearch(self):
        print self._api.search("*")


if __name__ == "__main__":
    unittest.main()
