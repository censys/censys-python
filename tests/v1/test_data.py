import unittest

import responses

from ..utils import CensysTestCase

from censys import SearchClient

SERIES_JSON = {
    "primary_series": "",
    "raw_series": "",
}
VIEW_JSON = {
    "description": (
        "The Censys IPv4 dataset provides data about the services "
        "(e.g., HTTP, SMTP, MySQL) running on all publicly-accessible IPv4 hosts."
    ),
    "results": {"historical": []},
}
RESULT_JSON = {"files": {"filename": {"file_type": "data"}}}
SERIES = "ipv4_2018"
RESULT = "20200818"


class CensysDataTest(CensysTestCase):
    def setUp(self):
        super().setUp()
        self.setUpApi(SearchClient(self.api_id, self.api_secret).v1.data)

    def test_get_series(self):
        self.responses.add(
            responses.GET,
            f"{self.base_url}/data",
            status=200,
            json=SERIES_JSON,
        )

        series = self.api.get_series()
        assert series == SERIES_JSON

    def test_view_series(self):
        self.responses.add(
            responses.GET,
            f"{self.base_url}/data/{SERIES}",
            status=200,
            json=VIEW_JSON,
        )
        res = self.api.view_series(SERIES)

        assert res == VIEW_JSON

    def test_view_result(self):
        self.responses.add(
            responses.GET,
            f"{self.base_url}/data/{SERIES}/{RESULT}",
            status=200,
            json=RESULT_JSON,
        )

        res = self.api.view_result(SERIES, RESULT)

        assert res == RESULT_JSON


if __name__ == "__main__":
    unittest.main()
