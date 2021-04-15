import datetime

import responses
from parameterized import parameterized

from ..utils import CensysTestCase
from .utils import (
    BASE_URL,
)

from censys.asm.client import AsmClient

HOST_COUNT_JSON = {
    "totalAssetCount": 0,
    "totalNewAssetCount": 0,
    "totalCloudAssetCount": 0,
    "totalCloudNewAssetCount": 0,
    "assetCountByProvider": [
        {"cloudProvider": "string", "assetCount": 0, "newAssetCount": 0}
    ],
}


class CloudsUnitTest(CensysTestCase):
    def setUp(self):
        super().setUp()
        self.client = AsmClient(self.api_key)

    @parameterized.expand(
        [
            ["2021-01-01", "2021-01-01"],
            [datetime.date(2021, 1, 1), "2021-01-01"],
            [datetime.datetime(2021, 1, 1, 12, 15, 20, 40), "2021-01-01"],
        ]
    )
    def test_get_host_counts(self, since, actual):
        self.responses.add(
            responses.GET,
            BASE_URL + f"/clouds/hostCounts/{actual}",
            status=200,
            json=HOST_COUNT_JSON,
        )

        res = self.client.clouds.get_host_counts(since)
        assert res == HOST_COUNT_JSON
