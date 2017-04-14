from __future__ import print_function
import unittest
import time
import json

from .base import CensysAPIBase


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

    VALID_QUERY = """SELECT ip FROM ipv4.20151012 where
    p443.https.tls.certificate.parsed.extensions.key_usage.certificate_sign=true
    order by ip desc"""
    LONG_QUERY = "select count(*) from FROM [ipv4.20170318] i WHERE i.location.country_code = \"FI\" AND (i.p80.http.get.body CONTAINS \"content=\"wordpress 4.7.2\" or i.p80.http.get.body CONTAINS \"content=\"WordPress 4.7.2\")"
    EMPTY_QUERY = "SELECT valid_nss FROM certificates.certificates where 1=0"
    INVALID_QUERY = "SELECT nvalid FROM certificates.certificates where 1=0"
    MULTIPLE_QUERY = "SELECT ip FROM ipv4.20151012 LIMIT 100; SELECT ip FROM ipv4.20151012 LIMIT 100"

    @classmethod
    def setUpClass(cls):
        cls._api = CensysQuery()

    #def test_query(self):
    #    j = self._api.new_job(self.VALID_QUERY)
    #    print(json.dumps(j))
    #    job_id = j["job_id"]
    #    r = self._api.check_job_loop(job_id)
    #    print(json.dumps(r))
    #    print(json.dumps(self._api.get_results(job_id, 1)))

    #def test_empty_query(self):
    #    j = self._api.new_job(self.EMPTY_QUERY)
    #    job_id = j["job_id"]
    #    r = self._api.check_job_loop(job_id)
    #    print(json.dumps(r))
    #    print(json.dumps(self._api.get_results(job_id, 1)))

    #def test_invalid_query(self):
    #    j = self._api.new_job(self.INVALID_QUERY)
    #    job_id = j["job_id"]
    #    r = self._api.check_job_loop(job_id)
    #    print(json.dumps(r))

    #def test_multiple_query(self):
    #    j = self._api.new_job(self.MULTIPLE_QUERY)
    #    job_id = j["job_id"]
    #    r = self._api.check_job_loop(job_id)
    #    print(json.dumps(r))

    #def test_get_series(self):
    #    print(self._api.get_series())

    #def test_get_series_details(self):
    #    print(self._api.get_series_details("ipv4"))

    def test_bad_loop(self):
        j = self._api.new_job(self.LONG_QUERY)
        job_id = j["job_id"]
        print(json.dumps(self._api.get_results(job_id, 1)))


if __name__ == "__main__":
    unittest.main()
