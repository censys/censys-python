import os
import unittest

import pytest
import responses

from censys.base import CensysAPIBase
from censys.config import DEFAULT, get_config

config = get_config()
api_id = config.get(DEFAULT, "api_id") or os.getenv("CENSYS_API_ID")
api_secret = config.get(DEFAULT, "api_secret") or os.getenv("CENSYS_API_SECRET")


required_env = pytest.mark.skipif(
    not (api_id and api_secret),
    reason="API credentials not found",
)

permissions_env = pytest.mark.skipif(
    not os.getenv("PERMISSIONS"),
    reason="(optional) enterprise permissions required",
)


# @required_env
# class CensysTestCase(unittest.TestCase):
#     pass
class CensysTestCase(unittest.TestCase):
    api_id = "test-api-id"
    api_secret = "test-api-secret"

    def setUp(self):
        self.responses = responses.RequestsMock()
        self.responses.start()

        self.addCleanup(self.responses.stop)
        self.addCleanup(self.responses.reset)

    def setUpApi(self, api: CensysAPIBase):
        self.api = api
        self.base_url = self.api._api_url
