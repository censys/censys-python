import unittest

import responses

from censys.common.base import CensysAPIBase

V1_URL = "https://censys.io/api/v1"
V2_URL = "https://search.censys.io/api/v2"


class CensysTestCase(unittest.TestCase):
    api_id = "test-api-id"
    api_secret = "test-api-secret"
    api_key = "test-api-key"
    cli_args = [
        "--api-id",
        api_id,
        "--api-secret",
        api_secret,
    ]

    def setUp(self):
        self.responses = responses.RequestsMock()
        self.responses.start()

        self.addCleanup(self.responses.stop)
        self.addCleanup(self.responses.reset)

    def setUpApi(self, api: CensysAPIBase):  # noqa: N802
        self.api = api
        self.base_url = self.api._api_url
