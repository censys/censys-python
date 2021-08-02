from typing import Callable

import pytest
import responses
from parameterized import parameterized

from tests.utils import CensysTestCase

from censys.search import SearchClient

VIEW_HOSTS_BY_CERT_JSON = {
    "code": 200,
    "status": "OK",
    "result": {
        "fp": "fb444eb8e68437bae06232b9f5091bccff62a768ca09e92eb5c9c2cf9d17c426",
        "hosts": [
            {
                "ip": "string",
                "name": "string",
                "observed_at": "2021-08-02T14:56:38.711Z",
                "first_observed_at": "2021-08-02T14:56:38.711Z",
            }
        ],
        "links": {"next": "nextCursorToken"},
    },
}

TEST_CERT = "fb444eb8e68437bae06232b9f5091bccff62a768ca09e92eb5c9c2cf9d17c426"


class TestCerts(CensysTestCase):
    def setUp(self):
        super().setUp()
        self.setUpApi(SearchClient(self.api_id, self.api_secret).v2.certs)

    @parameterized.expand([("view"), ("search"), ("aggregate"), ("metadata")])
    def test_not_implemented_methods(self, function_name: str):
        func: Callable = getattr(self.api, function_name)
        args = [""] * (func.__code__.co_argcount - 1)
        with pytest.raises(NotImplementedError):
            func(*args)

    def test_get_hosts_by_cert(self):
        self.responses.add(
            responses.GET,
            f"{self.base_url}/certificates/{TEST_CERT}/hosts",
            status=200,
            json=VIEW_HOSTS_BY_CERT_JSON,
        )
        results, links = self.api.get_hosts_by_cert(TEST_CERT)
        assert results == VIEW_HOSTS_BY_CERT_JSON["result"]["hosts"]
        assert links == VIEW_HOSTS_BY_CERT_JSON["result"]["links"]

    def test_get_hosts_by_cert_with_cursor(self):
        self.responses.add(
            responses.GET,
            f"{self.base_url}/certificates/{TEST_CERT}/hosts?cursor=nextCursorToken",
            status=200,
            json=VIEW_HOSTS_BY_CERT_JSON,
        )
        results, _ = self.api.get_hosts_by_cert(TEST_CERT, cursor="nextCursorToken")
        assert results == VIEW_HOSTS_BY_CERT_JSON["result"]["hosts"]
