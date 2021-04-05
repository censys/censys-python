import unittest
from unittest.mock import patch, mock_open

import requests_mock
from requests.models import Response
from parameterized import parameterized

from utils import CensysTestCase

from censys.base import CensysAPIBase
from censys.api import CensysSearchAPI
from censys.asm.api import CensysAsmAPI
from censys.exceptions import (
    CensysException,
    CensysAPIException,
    CensysSearchException,
    CensysAsmException,
    CensysExceptionMapper,
)


class CensysAPIBaseTests(CensysTestCase):
    HTTP_PROXY = "http://10.10.1.10:3128"
    HTTPS_PROXY = "http://10.10.1.10:1080"
    PROXIES = {
        "http": HTTP_PROXY,
        "https": HTTPS_PROXY,
    }
    ACCOUNT_URL = "https://censys.io/api/v1/account"
    ACCOUNT_JSON = {
        "email": "support@censys.io",
        "first_login": "",
        "last_login": "",
        "login": "support@censys.io",
        "quota": {},
    }

    @requests_mock.Mocker(kw="mock")
    def test_proxies(self, mock=None):
        mock.get(
            self.ACCOUNT_URL,
            json=self.ACCOUNT_JSON,
        )

        proxies = {"https": self.HTTPS_PROXY}
        api = CensysSearchAPI(proxies=proxies)
        api.account()

        self.assertDictEqual(proxies, mock.last_request.proxies)

    @requests_mock.Mocker(kw="mock")
    def test_warn_http_proxies(self, mock=None):
        mock.get(
            self.ACCOUNT_URL,
            json=self.ACCOUNT_JSON,
        )

        with self.assertWarns(UserWarning):
            api = CensysSearchAPI(proxies=self.PROXIES)
            api.account()

        self.assertDictEqual({"https": self.HTTPS_PROXY}, mock.last_request.proxies)

    def test_base_get_exception_class(self):
        base = CensysAPIBase("url")

        self.assertEqual(base._get_exception_class(Response()), CensysAPIException)

    @patch.dict("os.environ", {"CENSYS_API_URL": ""})
    def test_no_api_url(self):
        with self.assertRaises(CensysException) as context:
            CensysAPIBase()

        self.assertIn("No API url configured.", str(context.exception))

    @patch("censys.base.requests.Session.get")
    def test_successful_empty_json_response(self, mock):
        mock_response = Response()
        mock_response.status_code = 200
        mock.return_value = mock_response
        base = CensysAPIBase("url")

        self.assertEqual({}, base._make_call(base._session.get, "endpoint"))


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

        self.assertSetEqual(set(res.keys()), self.EXPECTED_ACCOUNT_KEYS)

    def test_quota(self):
        res = self._api.quota()

        self.assertSetEqual(set(res.keys()), self.EXPECTED_QUOTA_KEYS)
        self.assertTrue(
            all(isinstance(value, int) for value in [res["allowance"], res["used"]])
        )

    @parameterized.expand(SearchExceptionParams)
    def test_get_exception_class(self, status_code, exception):
        response = Response()
        response.status_code = status_code

        self.assertEqual(self._api._get_exception_class(response), exception)

    def test_exception_repr(self):
        exception = CensysSearchException(404, "Not Found", const="notfound")

        self.assertEqual(repr(exception), "404 (notfound): Not Found")


class CensysAsmAPITests(CensysTestCase):

    AsmExceptionParams = [
        (code, exception)
        for code, exception in CensysExceptionMapper.ASM_EXCEPTIONS.items()
    ]

    @parameterized.expand(AsmExceptionParams)
    @patch("requests.models.Response.json")
    def test_get_exception_class(self, status_code, exception, mock):
        response = Response()
        mock.return_value = {"errorCode": status_code}

        self.assertEqual(CensysAsmAPI()._get_exception_class(response), exception)

    def test_exception_repr(self):
        exception = CensysAsmException(
            404, "Unable to Find Seed", error_code=10014, details="[{id: 999}]"
        )

        self.assertEqual(
            repr(exception), "404 (Error Code: 10014), Unable to Find Seed. [{id: 999}]"
        )


@patch.dict("os.environ", {"CENSYS_API_ID": "", "CENSYS_API_SECRET": ""})
class CensysAPIBaseTestsNoSearchEnv(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data="[DEFAULT]")
    def test_no_env(self, mock_file):
        with self.assertRaises(CensysException) as context:
            CensysSearchAPI()

        self.assertIn("No API ID or API secret configured.", str(context.exception))


@patch.dict("os.environ", {"CENSYS_ASM_API_KEY": ""})
class CensysAPIBaseTestsNoAsmEnv(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data="[DEFAULT]")
    def test_no_env(self, mock_file):
        with self.assertRaises(CensysException) as context:
            CensysAsmAPI()

        self.assertIn("No ASM API key configured.", str(context.exception))


if __name__ == "__main__":
    unittest.main()
