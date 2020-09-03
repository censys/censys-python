import unittest

from utils import CensysTestCase

from censys.certificates import CensysCertificates


class CensysCertificatesTests(CensysTestCase):

    CERT_SHA = "fce621c0dc1c666d03d660472f636ce91e66e96460545f0da7eb1a24873e2f70"

    @classmethod
    def setUpClass(cls):
        cls._api = CensysCertificates()

    def test_view(self):
        response = self._api.view(self.CERT_SHA)
        self.assertIsInstance(response, dict)
        self.assertEqual(response["parsed"]["fingerprint_sha256"], self.CERT_SHA)

    def test_search(self):
        response = list(
            self._api.search(
                self.CERT_SHA,
                fields=["parsed.subject_dn", "parsed.fingerprint_sha256"],
                max_records=1,
            )
        )
        self.assertEqual(len(response), 1)
        self.assertIn("parsed.subject_dn", response[0])
        self.assertIn("parsed.fingerprint_sha256", response[0])

    def test_bulk(self):
        response = self._api.bulk([self.CERT_SHA])

        self.assertEqual(len(response.keys()), 1)
        self.assertIn(self.CERT_SHA, response)

    # def testMultiplePages(self):
    #     q = "parsed.extensions.basic_constraints.is_ca: true AND parsed.signature.self_signed: false"
    #     x = self._api.search(q, page=1)
    #     y = self._api.search(q, page=2)
    #     self.assertNotEqual(list(x), list(y))

    # def testReport(self):
    #    print self._api.report("*", "parsed.subject_key_info.key_algorithm.name")


if __name__ == "__main__":
    unittest.main()
