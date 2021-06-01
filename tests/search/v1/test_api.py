import unittest
from unittest.mock import mock_open, patch

import pytest
import responses
from parameterized import parameterized
from requests.models import Response

from tests.utils import CensysTestCase

from censys.common.exceptions import (
    CensysException,
    CensysExceptionMapper,
    CensysSearchException,
)
from censys.search.v1.api import CensysSearchAPI

ACCOUNT_JSON = {
    "login": "test@censys.io",
    "first_login": "2021-01-01 01:00:00",
    "last_login": "2021-01-01 01:00:00.000000",
    "email": "test@censys.io",
    "quota": {"used": 1, "resets_at": "2021-01-01 01:00:00", "allowance": 100},
}

SearchExceptionParams = [
    (code, exception)
    for code, exception in CensysExceptionMapper.SEARCH_EXCEPTIONS.items()
]


class CensysSearchAPITests(CensysTestCase):
    def setUp(self):
        super().setUp()
        self.setUpApi(CensysSearchAPI(self.api_id, self.api_secret))

    def test_account(self):
        self.responses.add(
            responses.GET,
            self.base_url + "/account",
            status=200,
            json=ACCOUNT_JSON,
        )
        res = self.api.account()

        assert res == ACCOUNT_JSON

    def test_quota(self):
        self.responses.add(
            responses.GET,
            self.base_url + "/account",
            status=200,
            json=ACCOUNT_JSON,
        )
        res = self.api.quota()

        assert res == ACCOUNT_JSON["quota"]

    @parameterized.expand(SearchExceptionParams)
    def test_get_exception_class(self, status_code, exception):
        response = Response()
        response.status_code = status_code

        assert self.api._get_exception_class(response) == exception

    def test_exception_repr(self):
        exception = CensysSearchException(404, "Not Found", const="notfound")

        assert repr(exception) == "404 (notfound): Not Found"


@patch.dict("os.environ", {"CENSYS_API_ID": "", "CENSYS_API_SECRET": ""})
class CensysAPIBaseTestsNoSearchEnv(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data="[DEFAULT]")
    def test_no_env(self, mock_file):
        with pytest.raises(
            CensysException, match="No API ID or API secret configured."
        ):
            CensysSearchAPI()
