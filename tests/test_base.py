import pytest
import requests.utils
import responses
from requests.models import Response

from .utils import CensysTestCase
from censys.common import __version__
from censys.common.base import CensysAPIBase
from censys.common.exceptions import CensysAPIException, CensysException

TEST_URL = "https://url"
TEST_ENDPOINT = "/endpoint"
ERROR_JSON = {
    "error": "Test Error",
    "error_type": "Test",
    "errorCode": 200,
    "details": "This is a test error",
}


class CensysAPIBaseTests(CensysTestCase):
    def test_base_get_exception_class(self):
        # Mock
        base = CensysAPIBase("url")
        # Actual call/assertions
        assert base._get_exception_class(Response()) == CensysAPIException

    def test_no_api_url(self):
        # Mock
        self.mocker.patch.dict("os.environ", {"CENSYS_API_URL": ""})
        # Actual call/error raising
        with pytest.raises(CensysException, match="No API url configured."):
            CensysAPIBase()

    def test_successful_empty_json_response(self):
        # Mock response
        self.responses.add(
            responses.GET,
            TEST_URL + TEST_ENDPOINT,
            status=200,
            body=None,
        )
        # Actual call
        base = CensysAPIBase(TEST_URL)
        # Assertions
        assert base._get(TEST_ENDPOINT) == {
            "status": "OK",
            "code": 200,
        }

    def test_successful_error_json_response(self):
        # Mock response
        self.responses.add(
            responses.GET,
            TEST_URL + TEST_ENDPOINT,
            status=200,
            json=ERROR_JSON,
        )
        # Actual call
        base = CensysAPIBase(TEST_URL)
        # Assertion/error raising
        with pytest.raises(CensysAPIException, match=ERROR_JSON["error"]):
            base._get(TEST_ENDPOINT)

    def test_invalid_json_response(self):
        # Mock response
        self.responses.add(
            responses.GET,
            TEST_URL + TEST_ENDPOINT,
            status=400,
            body="<html><h1>Definitely not JSON</h1>",
        )
        # Actual call
        base = CensysAPIBase(TEST_URL)
        # Assertion/error raising
        with pytest.raises(
            CensysAPIException, match="is not valid JSON and cannot be decoded"
        ):
            base._get(TEST_ENDPOINT)

    def test_default_user_agent(self):
        # Mock/actual call
        base = CensysAPIBase(TEST_URL)
        # Assertions
        assert (
            base._session.headers["User-Agent"]
            == f"{requests.utils.default_user_agent()} censys-python/{__version__}"
        )

    def test_user_agent(self):
        # Mock/actual call
        base = CensysAPIBase(TEST_URL, user_agent="test")
        # Assertions
        assert (
            base._session.headers["User-Agent"]
            == requests.utils.default_user_agent() + " test"
        )

    def test_request_id(self):
        id_value = "my-request-id"

        # Test request id value is present
        base = CensysAPIBase(TEST_URL, request_id=id_value)
        assert base.request_id == id_value
        assert base._session.headers.get("x-request-id") == id_value

        # Test request id value is not present
        base.request_id = None
        assert base.request_id is None
        assert base._session.headers.get("x-request-id") is None

    @pytest.mark.filterwarnings("ignore:HTTP proxies will not be used.")
    def test_proxies(self):
        # Mock/actual call
        base = CensysAPIBase(TEST_URL, proxies={"http": "test", "https": "tests"})
        # Assertions
        assert list(base._session.proxies.keys()) == ["https"]

    def test_cookies(self):
        # Mock/actual call
        base = CensysAPIBase(TEST_URL, cookies={"_ga": "GA"})
        # Assertions
        assert list(base._session.cookies.keys()) == ["_ga"]

    def test_verify_and_cert(self):
        # Mock/actual call
        base = CensysAPIBase(
            TEST_URL, 
            cert=("/path/to/clientcert", "/path/to/clientkey"), 
            verify="/path/to/cacert"
        )
        assert base._session.cert == ("/path/to/clientcert", "/path/to/clientkey")
        assert base._session.verify == "/path/to/cacert"
