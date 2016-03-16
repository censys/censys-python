from __future__ import print_function
import unittest

from .base import CensysAPIBase


class CensysWebsites(CensysAPIBase):

    def search(self, query, fields=None):
        if fields is None:
            fields = []
        page = 1
        pages = float('inf')
        data = {
            "query": query,
            "page": page,
            "fields": fields
        }

        while page <= pages:
            payload = self._post("search/websites", data=data)
            pages = payload['metadata']['pages']
            page += 1
            data["page"] = page

            for result in payload["results"]:
                yield result

    def view(self, domain):
        return self._get("/".join(("view", "websites", domain)))

    def report(self, query, field, buckets=50):
        data = {
            "query": query,
            "field": field,
            "buckets": int(buckets)
        }
        return self._post("report/websites", data=data)


class CensysWebsitesTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._api = CensysWebsites()

    def testGet(self):
        print(self._api.view("google.com"))

    def testSearch(self):
        print(self._api.search("*"))

    def testReport(self):
        print(self._api.report("*", "80.http.get.headers.server.raw"))


if __name__ == "__main__":
    unittest.main()
