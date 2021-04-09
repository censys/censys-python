import unittest
from unittest.mock import patch, mock_open

import pytest
from requests.models import Response
from parameterized import parameterized

from ..utils import CensysTestCase

from censys.v1.api import CensysSearchAPI
from censys.exceptions import (
    CensysException,
    CensysSearchException,
    CensysExceptionMapper,
)


class CensysSearchAPITests(CensysTestCase):

    EXPECTED_ACCOUNT_KEYS = {"email", "first_login", "last_login", "login", "quota"}
    EXPECTED_QUOTA_KEYS = {"allowance", "resets_at", "used"}
    SearchExceptionParams = [
        (code, exception)
        for code, exception in CensysExceptionMapper.SEARCH_EXCEPTIONS.items()
    ]

    @classmethod
    def setUpClass(cls):
        cls._api = CensysSearchAPI()

    def test_account(self):
        res = self._api.account()

        assert set(res.keys()) == self.EXPECTED_ACCOUNT_KEYS

    def test_quota(self):
        res = self._api.quota()

        assert set(res.keys()) == self.EXPECTED_QUOTA_KEYS
        assert all(isinstance(value, int) for value in [res["allowance"], res["used"]])

    @parameterized.expand(SearchExceptionParams)
    def test_get_exception_class(self, status_code, exception):
        response = Response()
        response.status_code = status_code

        assert self._api._get_exception_class(response) == exception

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


if __name__ == "__main__":
    unittest.main()
