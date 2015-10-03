import time
from censys.censys import *

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
        return self._post("export", body=body)

    def check_job(self, export_id):
        path = "/".join("export", export_id)
        return self._get(path)

    def check_job_loop(self, export_id):
        while True:
            res = self.check_job(export_id)
            if res["status"] != "pending":
                return res
            time.sleep(1)
          
