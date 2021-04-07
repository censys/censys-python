import unittest

from ..utils import CensysTestCase

from censys.v1.certificates import CensysCertificates


class CensysCertificatesTests(CensysTestCase):

    CERT_SHA = "fce621c0dc1c666d03d660472f636ce91e66e96460545f0da7eb1a24873e2f70"

    @classmethod
    def setUpClass(cls):
        cls._api = CensysCertificates()

    def test_view(self):
        res = self._api.view(self.CERT_SHA)
        self.assertIsInstance(res, dict)
        self.assertEqual(res["parsed"]["fingerprint_sha256"], self.CERT_SHA)

    def test_search(self):
        res = list(
            self._api.search(
                self.CERT_SHA,
                fields=["parsed.subject_dn", "parsed.fingerprint_sha256"],
                max_records=1,
            )
        )
        self.assertEqual(len(res), 1)
        self.assertIn("parsed.subject_dn", res[0])
        self.assertIn("parsed.fingerprint_sha256", res[0])

    def test_bulk(self):
        res = self._api.bulk([self.CERT_SHA])
        self.assertEqual(len(res.keys()), 1)
        self.assertIn(self.CERT_SHA, res)

    def test_report(self):
        res = self._api.report("*", "parsed.issuer.organizational_unit", buckets=10)
        results = res.get("results")
        self.assertEqual(len(results), 10)


if __name__ == "__main__":
    unittest.main()
