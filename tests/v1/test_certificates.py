import unittest

import responses

from ..utils import CensysTestCase

from censys import SearchClient

BULK_JSON = {
    "fce621c0dc1c666d03d660472f636ce91e66e96460545f0da7eb1a24873e2f70": "MISC_CERT_DATA",
    "a762bf68f167f6fbdf2ab00fdefeb8b96f91335ad6b483b482dfd42c179be076": "MISC_CERT_DATA",
}


class CensysCertificatesTests(CensysTestCase):
    def setUp(self):
        super().setUp()
        self.setUpApi(
            SearchClient(api_id=self.api_id, api_secret=self.api_secret).v1.certificates
        )

    def test_bulk(self):
        self.responses.add(
            responses.POST,
            f"{self.base_url}/bulk/certificates",
            status=200,
            json=BULK_JSON,
        )

        res = self.api.bulk(
            [
                "fce621c0dc1c666d03d660472f636ce91e66e96460545f0da7eb1a24873e2f70",
                "a762bf68f167f6fbdf2ab00fdefeb8b96f91335ad6b483b482dfd42c179be076",
            ]
        )

        assert res == BULK_JSON


if __name__ == "__main__":
    unittest.main()
