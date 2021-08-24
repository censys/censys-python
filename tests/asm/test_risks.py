import responses
from parameterized import parameterized

from ..utils import CensysTestCase
from .utils import BASE_URL
from censys.asm.client import AsmClient

TEST_RISKS_JSON = {
    "pageNumber": 0,
    "pageSize": 0,
    "totalPages": 0,
    "totalItems": 0,
    "environment": "string",
    "data": [
        {
            "riskInfoId": 0,
            "name": "string",
            "severity": "accepted",
            "isSeverityModified": True,
            "categories": ["string"],
            "affectedAssetsCount": 0,
            "assetType": "HOST",
        },
        {
            "riskInfoId": 0,
            "name": "string",
            "severity": "accepted",
            "isSeverityModified": True,
            "categories": ["string"],
            "affectedAssetsCount": 0,
            "assetType": "DOMAIN",
        },
        {
            "riskInfoId": 0,
            "name": "string",
            "severity": "accepted",
            "isSeverityModified": True,
            "categories": ["string"],
            "affectedAssetsCount": 0,
            "assetType": "CERT",
        },
        {
            "riskInfoId": 0,
            "name": "string",
            "severity": "accepted",
            "isSeverityModified": True,
            "categories": ["string"],
            "affectedAssetsCount": 0,
            "assetType": "STORAGE_BUCKET",
        },
    ],
}


class CloudsUnitTest(CensysTestCase):
    def setUp(self):
        super().setUp()
        self.client = AsmClient(self.api_key)

    @parameterized.expand(
        [
            ({}, ""),
            ({"cloud": "Amazon AWS"}, "&cloud=Amazon AWS"),
            ({"environment": "CLOUD"}, "&environment=CLOUD"),
            ({"include_accepted_risks": True}, "&includeAcceptedRisks=True"),
        ]
    )
    def test_get_risks(self, kwargs, params):
        self.responses.add(
            responses.GET,
            BASE_URL + f"/risks?pageNumber=1&pageSize=100{params}",
            status=200,
            json=TEST_RISKS_JSON,
        )

        res = list(self.client.risks.get_risks(**kwargs))
        assert res == TEST_RISKS_JSON["data"]
