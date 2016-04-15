from __future__ import print_function
import json
import sys
import unittest
import time

from .base import CensysAPIBase


class CensysExport(CensysAPIBase):

    def new_job(self, query, format="json", flatten=False, compress=False,
                delimiter=None, headers=None):
        assert format in ("json", "csv")
        assert flatten in (True, False)
        assert compress in (True, False)
        data = {
            "query": query,
            "format": format,
            "flatten": flatten,
            "compress": compress,
            "delimiter": delimiter,
            "headers": headers
        }
        return self._post("export", data=data)

    def check_job(self, job_id):
        path = "/".join(("export", job_id))
        return self._get(path)

    def check_job_loop(self, job_id):
        while True:
            res = self.check_job(job_id)
            if res["status"] != "pending":
                return res
            time.sleep(1)


class CensysExportTests(unittest.TestCase):
    VALID_QUERY = "select * from certificates.certificates limit 1000"
    INVALID_QUERY = "select dne from ipv4.20150902 limit 1000"

    def setUp(self):
        self._api = CensysExport()

    def test_query(self):
        j = self._api.new_job(self.VALID_QUERY)
        if j["status"] not in ("success", "pending"):
            print(j)
            sys.exit(1)
        job_id = j["job_id"]
        r = self._api.check_job_loop(job_id)
        print(json.dumps(r))


if __name__ == "__main__":
    unittest.main()
