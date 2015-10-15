import json
from censys import * 

class CensysCertificates(CensysAPIBase):

    def search(self, query, page=1, fields=[]):
        data = {
            "query":query,
            "page":page,
            "fields":fields
        }
        return self._post("search/certificates", data=data)

    def view(self, sha256fp):
        return self._get("/".join(("view", "certificates", sha256fp)))

    def report(self, query, field, buckets):
        pass



class CensysCertificatesTests(unittest.TestCase):

    def setUp(self):
        self._api = CensysCertificates()

    def testGet(self):
        print json.dumps(self._api.view("fce621c0dc1c666d03d660472f636ce91e66e96460545f0da7eb1a24873e2f70"))

    def testSearch(self):
        print self._api.search("*")


if __name__ == "__main__":
    unittest.main()
