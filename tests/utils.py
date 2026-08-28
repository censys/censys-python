from typing import Optional

import pytest
import responses
from pytest_mock import MockerFixture

from censys.common.base import CensysAPIBase

BASE_URL = "https://search.censys.io/api"
V1_URL = BASE_URL + "/v1"
V2_URL = BASE_URL + "/v2"


class CensysTestCase:
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
    def _setup(self, mocker: MockerFixture):
        self.mocker = mocker
        mocker.patch("time.sleep", return_value=None)
        rsps = responses.RequestsMock(assert_all_requests_are_fired=False)
        rsps.start()
        self.responses = rsps
        yield
        rsps.stop()
        rsps.reset()

    def setUpApi(self, api: CensysAPIBase):  # noqa: N802
        self.api = api
        self.base_url = self.api._api_url

    def patch_args(
        self,
        args: list[str],
        search_auth: Optional[bool] = False,
        asm_auth: Optional[bool] = False,
    ):
        if search_auth:
            args.extend(self.cli_args)
        if asm_auth:
            args.extend(self.asm_cli_args)

        self.mocker.patch("argparse._sys.argv", args)
