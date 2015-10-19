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

    def report(self, query, field, buckets=50):
        data = {
            "query":query,
            "field":field,
            "buckets":int(buckets)
        }
        return self._post("report/websites", data=data)


class CensysWebsitesTests(unittest.TestCase):

    def setUp(self):
        self._api = CensysWebsites()

    def testGet(self):
        print self._api.view("google.com")

    def testSearch(self):
        print self._api.search("*")

    def testReport(self):
        print self._api.report("*", "80.http.get.headers.server.raw")


if __name__ == "__main__":
    unittest.main()

