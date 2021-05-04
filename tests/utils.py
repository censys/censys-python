import unittest

import responses

from censys.common.base import CensysAPIBase


class CensysTestCase(unittest.TestCase):
    api_id = "test-api-id"
    api_secret = "test-api-secret"
    api_key = "test-api-key"

    def setUp(self):
        self.responses = responses.RequestsMock()
        self.responses.start()

        self.addCleanup(self.responses.stop)
        self.addCleanup(self.responses.reset)

    def setUpApi(self, api: CensysAPIBase):  # noqa: N802
        self.api = api
        self.base_url = self.api._api_url
