from __future__ import print_function
import unittest
import time

from censys import CensysAPIBase


class CensysQuery(CensysAPIBase):

    def new_job(self, query):
        data = {"query": query}
        return self._post("query", data=data)

    def get_series(self):
        path = "/query_definitions"
        return self._get(path)

    def get_series_details(self, series):
        path = "/".join(("query_definitions", series))
        return self._get(path)

    def check_job(self, job_id):
        path = "/".join(("query", job_id))
        return self._get(path)

    def check_job_loop(self, job_id):
        while True:
            res = self.check_job(job_id)
            if res["status"] != "pending":
                return res
            time.sleep(1)

    def get_results(self, job_id, page=1):
        path = "/".join(("query", job_id, str(page)))
        return self._get(path)


class CensysQueryTests(unittest.TestCase):
    VALID_QUERY = "select ip,updated_at, zdb_version, ipint from ipv4.20150902 limit 5300"

    @classmethod
    def setUpClass(cls):
        cls._api = CensysQuery()

    #    def test_query(self):
    #        j = self._api.new_job(self.VALID_QUERY)
    #        print json.dumps(j)
    #        job_id = j["job_id"]
    #        r = self._api.check_job_loop(job_id)
    #        print json.dumps(r)
    #        print json.dumps(self._api.get_results(job_id, 2))
    #
    def test_get_series(self):
        print(self._api.get_series())

    def test_get_series_details(self):
        print(self._api.get_series_details("ipv4"))


if __name__ == "__main__":
    unittest.main()
