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

        assert isinstance(res, dict)
        assert res["parsed"]["fingerprint_sha256"] == self.CERT_SHA

    def test_search(self):
        res = list(
            self._api.search(
                self.CERT_SHA,
                fields=["parsed.subject_dn", "parsed.fingerprint_sha256"],
                max_records=1,
            )
        )

        assert len(res) == 1
        assert "parsed.subject_dn" in res[0]
        assert "parsed.fingerprint_sha256" in res[0]

    def test_bulk(self):
        res = self._api.bulk([self.CERT_SHA])

        assert len(res.keys()) == 1
        assert self.CERT_SHA in res

    def test_report(self):
        res = self._api.report("*", "parsed.issuer.organizational_unit", buckets=10)
        results = res.get("results")

        assert len(results) == 10


if __name__ == "__main__":
    unittest.main()
