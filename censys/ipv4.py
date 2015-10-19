import json
import struct
import socket
import unittest
from censys import *

class CensysIPv4(CensysAPIBase):

    def search(self, query, page=1, fields=[]):
        data = {
            "query":query,
            "page":page,
            "fields":fields
        }
        return self._post("search/ipv4", data=data)

    @staticmethod
    def convert_ip(ip):
        return int(socket.inet_aton(ip).encode('hex'),16)

    def view(self, ip):
        if type(ip) in (str, unicode):
            ip = self.convert_ip(ip)
        return self._get("/".join(("view", "ipv4", str(ip))))

    def report(self, query, field, buckets=50):
        data = {
            "query":query,
            "field":field,
            "buckets":int(buckets)
        }
        return self._post("report/ipv4", data=data)



class CensysIPv4Tests(unittest.TestCase):

    def setUp(self):
        self._api = CensysIPv4()

    def testGet(self):
        print json.dumps(self._api.view("84.206.102.184"))
        print "\n\n\n"

    def testSearch(self):
        print json.dumps(self._api.search("*"))
        print "\n\n\n"

    #def testInvalidSearch(self):
    #    print json.dumps(self._api.search('"'))
    #    print "\n\n\n"


    def testReport(self):
        print json.dumps(self._api.report("*", "protocols", 5))
        print "\n\n\n"


if __name__ == "__main__":
    unittest.main()
