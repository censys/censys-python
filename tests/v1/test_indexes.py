import unittest

import pytest
import responses
from parameterized import parameterized_class

from ..utils import CensysTestCase

from censys import CensysCertificates, CensysIPv4, CensysWebsites
from censys.exceptions import CensysException

VIEW_JSON = {
    "document": "test_id",
    "tags": ["http", "https"],
    "ports": [80, 443],
    "protocols": [
        "443/https_www",
        "80/http",
        "80/http_www",
        "443/https",
    ],
}
SEARCH_JSON = {
    "status": "ok",
    "results": [{}],
    "metadata": {
        "count": 10000,
        "query": "*",
        "page": 1,
        "pages": 1,
    },
}
REPORT_JSON = {
    "status": "ok",
    "results": [
        {"key": "cloudflare", "doc_count": 199512},
        {"key": "Apache", "doc_count": 150828},
        {"key": "nginx", "doc_count": 138877},
    ],
    "metadata": {
        "count": 958646,
        "backend_time": 172,
        "nonnull_count": 813207,
        "other_result_count": 323990,
        "buckets": 3,
        "error_bound": 6519,
        "query": "*",
    },
}


@parameterized_class(
    ("index", "index_wrapper", "document_id"),
    [
        (
            "certificates",
            CensysCertificates,
            "fce621c0dc1c666d03d660472f636ce91e66e96460545f0da7eb1a24873e2f70",
        ),
        ("ipv4", CensysIPv4, "8.8.8.8"),
        ("websites", CensysWebsites, "google.com"),
    ],
)
class CensysIndexTests(CensysTestCase):
    def setUp(self):
        super().setUp()
        self.setUpApi(
            self.index_wrapper(api_id=self.api_id, api_secret=self.api_secret)
        )

    def test_view(self):
        self.responses.add(
            responses.GET,
            f"{self.base_url}/view/{self.index}/{self.document_id}",
            status=200,
            json=VIEW_JSON,
        )

        res = self.api.view(self.document_id)

        assert res == VIEW_JSON

    def test_search(self):
        self.responses.add(
            responses.POST,
            f"{self.base_url}/search/{self.index}",
            status=200,
            json=SEARCH_JSON,
        )

        res = list(self.api.search("*"))

        assert res == SEARCH_JSON["results"]

    def test_report(self):
        self.responses.add(
            responses.POST,
            f"{self.base_url}/report/{self.index}",
            status=200,
            json=REPORT_JSON,
        )

        res = self.api.report("*", "80.http.get.headers.server.raw", buckets=3)

        assert res == REPORT_JSON

    def test_metadata(self):
        self.responses.add(
            responses.POST,
            f"{self.base_url}/search/{self.index}",
            status=200,
            json=SEARCH_JSON,
        )

        res = self.api.metadata("*")

        assert res == SEARCH_JSON["metadata"]

    def test_bad_page_search(self):
        with pytest.raises(CensysException, match="Invalid page value: x"):
            list(self.api.search("*", page="x"))


if __name__ == "__main__":
    unittest.main()
