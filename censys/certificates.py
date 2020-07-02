import unittest

from .base import CensysAPIBase, CensysIndex, CensysException


class CensysCertificates(CensysIndex):

    INDEX_NAME = "certificates"
    MAX_PER_BULK_REQUEST = 50

    def __init__(self, *args, **kwargs):
        CensysIndex.__init__(self, *args, **kwargs)
        self.bulk_path = "/bulk/{}".format(self.INDEX_NAME)

    def bulk(self, fingerprints):
        result = dict()
        start = 0
        end = self.MAX_PER_BULK_REQUEST
        while start < len(fingerprints):
            data = {
                "fingerprints": fingerprints[start:end]
            }
            result.update(self._post(self.bulk_path,data=data))
            start = end
            end += self.MAX_PER_BULK_REQUEST

        return result


class CensysCertificatesTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._api = CensysCertificates()

    def testGet(self):
        queriedFp = "fce621c0dc1c666d03d660472f636ce91e66e96460545f0da7eb1a24873e2f70"
        res = self._api.view(queriedFp)
        self.assertIsInstance(res, dict)
        self.assertEqual(res["parsed"]["fingerprint_sha256"], queriedFp)
        

    def testSearch(self):
        # searching for something that won't change hopefully
        x = self._api.search("fce621c0dc1c666d03d660472f636ce91e66e96460545f0da7eb1a24873e2f70", 
                            fields=["parsed.subject_dn",
                                    "parsed.fingerprint_sha256"],
                            max_records=1)
        result = list(x)
        self.assertEqual(len(result), 1)
        self.assertIn("parsed.subject_dn", result[0])
        self.assertIn("parsed.fingerprint_sha256", result[0])

    def testBulk(self):
        x = self._api.bulk(["fce621c0dc1c666d03d660472f636ce91e66e96460545f0da7eb1a24873e2f70"])

        self.assertEqual(len(x.keys()), 1)
        self.assertIn("fce621c0dc1c666d03d660472f636ce91e66e96460545f0da7eb1a24873e2f70", x)

    # def testMultiplePages(self):
    #     q = "parsed.extensions.basic_constraints.is_ca: true AND parsed.signature.self_signed: false"
    #     x = self._api.search(q, page=1)
    #     y = self._api.search(q, page=2)
    #     self.assertNotEqual(list(x), list(y))

    # def testReport(self):
    #    print self._api.report("*", "parsed.subject_key_info.key_algorithm.name")


if __name__ == "__main__":
    unittest.main()
