import unittest
from typing import Type
from unittest.mock import mock_open, patch

import pytest
import responses
from parameterized import parameterized
from requests.models import Response

from tests.search.v1.test_api import ACCOUNT_JSON
from tests.utils import V1_ENDPOINT_ON_V2_URL, CensysTestCase

from censys.common.exceptions import CensysException, CensysExceptionMapper
from censys.search.v2.api import CensysSearchAPIv2

SearchExceptionParams = [
    (code, exception)
    for code, exception in CensysExceptionMapper.SEARCH_EXCEPTIONS.items()
]


class CensysSearchAPITests(CensysTestCase):
    api: Type[CensysSearchAPIv2]

    def setUp(self):
        super().setUp()
        self.setUpApi(CensysSearchAPIv2(self.api_id, self.api_secret))

    @parameterized.expand(SearchExceptionParams)
    def test_get_exception_class(self, status_code, exception):
        response = Response()
        response.status_code = status_code

        assert self.api._get_exception_class(response) == exception

    def test_account_and_quota(self):
        self.responses.add(
            responses.GET,
            f"{V1_ENDPOINT_ON_V2_URL}/account",
            status=200,
            json=ACCOUNT_JSON,
        )
        results = self.api.account()
        assert results == ACCOUNT_JSON

        results = self.api.quota()
        assert results == ACCOUNT_JSON["quota"]

    def test_v1_endpoint_on_v2_url(self):
        # Asserts that the API URL was set correctly
        assert self.api.v1._api_url == V1_ENDPOINT_ON_V2_URL

        # Asserts that proxies get set correctly
        api_with_proxy = CensysSearchAPIv2(
            self.api_id, self.api_secret, proxies={"https": "test.proxy.com"}
        )
        assert list(api_with_proxy.v1._session.proxies.keys()) == ["https"]

        # Asserts that cookies get set correctly
        api_with_cookies = CensysSearchAPIv2(
            self.api_id, self.api_secret, cookies={"_ga": "GA"}
        )
        assert list(api_with_cookies.v1._session.cookies.keys()) == ["_ga"]


@patch.dict("os.environ", {"CENSYS_API_ID": "", "CENSYS_API_SECRET": ""})
class CensysAPIBaseTestsNoSearchEnv(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data="[DEFAULT]")
    def test_no_env(self, mock_file):
        with pytest.raises(
            CensysException, match="No API ID or API secret configured."
        ):
            CensysSearchAPIv2()
