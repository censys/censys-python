from unittest.mock import patch

import pytest
import responses
from requests.models import Response

from .utils import CensysTestCase

from censys.common.base import CensysAPIBase
from censys.common.exceptions import (
    CensysException,
    CensysAPIException,
)

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
        base = CensysAPIBase("url")

        assert base._get_exception_class(Response()) == CensysAPIException

    @patch.dict("os.environ", {"CENSYS_API_URL": ""})
    def test_no_api_url(self):
        with pytest.raises(CensysException, match="No API url configured."):
            CensysAPIBase()

    def test_successful_empty_json_response(self):
        self.responses.add(
            responses.GET,
            TEST_URL + TEST_ENDPOINT,
            status=200,
            body=None,
        )
        base = CensysAPIBase(TEST_URL)

        assert base._get(TEST_ENDPOINT) == {}

    def test_successful_error_json_response(self):
        self.responses.add(
            responses.GET,
            TEST_URL + TEST_ENDPOINT,
            status=200,
            json=ERROR_JSON,
        )
        base = CensysAPIBase(TEST_URL)

        with pytest.raises(CensysAPIException, match=ERROR_JSON["error"]):
            base._get(TEST_ENDPOINT)

    def test_invalid_json_response(self):
        self.responses.add(
            responses.GET,
            TEST_URL + TEST_ENDPOINT,
            status=400,
            body="<html><h1>Definitely not JSON</h1>",
        )
        base = CensysAPIBase(TEST_URL)

        with pytest.raises(
            CensysAPIException, match="is not valid JSON and cannot be decoded"
        ):
            base._get(TEST_ENDPOINT)

    def test_proxies(self):
        base = CensysAPIBase(TEST_URL, proxies={"http": "test", "https": "tests"})
        assert list(base._session.proxies.keys()) == ["https"]
