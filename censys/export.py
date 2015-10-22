import unittest
import time
from censys import *

class CensysExport(CensysAPIBase):

    def new_job(self, query, format="json", flatten=False, compress=False):
        assert format in ("json", "csv")
        assert flatten in (True, False)
        assert compress in (True, False)
        data = {
            "query":query,
            "format":format,
            "flatten":flatten,
            "compress":compress,
        }
        return self._post("export", data=data)

    def check_job(self, export_id):
        path = "/".join(("export", export_id))
        return self._get(path)

    def check_job_loop(self, export_id):
        while True:
            res = self.check_job(export_id)
            if res["status"] != "pending":
                return res
            time.sleep(1)


class CensysExportTests(unittest.TestCase):

    VALID_QUERY = "select * from ipv4.20150902 limit 1000"
    INVALID_QUERY = "select dne from ipv4.20150902 limit 1000"

    def setUp(self):
        self._api = CensysExport()

    def test_query(self):
        j = self._api.new_job(self.VALID_QUERY)
        export_id = j["export_id"]
        r = self._api.check_job_loop(export_id)
        print r

if __name__ == "__main__":
    unittest.main()
