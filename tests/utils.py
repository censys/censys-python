import unittest

import pytest
import responses
from pytest_mock import MockerFixture

from censys.common.base import CensysAPIBase

BASE_URL = "https://search.censys.io/api"
V1_URL = BASE_URL + "/v1"
V2_URL = BASE_URL + "/v2"


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
    asm_cli_args = [
        "--api-key",
        api_key,
    ]
    api: CensysAPIBase
    mocker: MockerFixture

    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker: MockerFixture):
        """Injects fixtures into the test case.

        Args:
            mocker (MockerFixture): pytest-mock fixture.
        """
        # Inject mocker fixture
        self.mocker = mocker

    def setUp(self):
        self.responses = responses.RequestsMock()
        self.responses.start()

        self.addCleanup(self.responses.stop)
        self.addCleanup(self.responses.reset)

    def setUpApi(self, api: CensysAPIBase):  # noqa: N802
        self.api = api
        self.base_url = self.api._api_url
