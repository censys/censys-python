import responses

from ..utils import CensysTestCase
from .utils import V1_URL
from censys.asm.client import AsmClient

TEST_COUNT_JSON = {
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

    def test_get_host_counts(self):
        # Setup response
        self.responses.add(
            responses.GET,
            V1_URL + "/clouds/hostCounts/2021-01-01",
            status=200,
            json=TEST_COUNT_JSON,
        )
        # Actual call
        res = self.client.clouds.get_host_counts("2021-01-01")
        # Assertions
        assert res == TEST_COUNT_JSON

    def test_get_domain_counts(self):
        # Setup response
        self.responses.add(
            responses.GET,
            V1_URL + "/clouds/domainCounts/2021-01-01",
            status=200,
            json=TEST_COUNT_JSON,
        )
        # Actual call
        res = self.client.clouds.get_domain_counts("2021-01-01")
        # Assertions
        assert res == TEST_COUNT_JSON

    def test_get_object_store_counts(self):
        # Setup response
        self.responses.add(
            responses.GET,
            V1_URL + "/clouds/objectStoreCounts/2021-01-01",
            status=200,
            json=TEST_COUNT_JSON,
        )
        # Actual call
        res = self.client.clouds.get_object_store_counts("2021-01-01")
        # Assertions
        assert res == TEST_COUNT_JSON

    def test_get_subdomain_counts(self):
        # Setup response
        self.responses.add(
            responses.GET,
            V1_URL + "/clouds/subdomainCounts/2021-01-01",
            status=200,
            json=TEST_COUNT_JSON,
        )
        # Actual call
        res = self.client.clouds.get_subdomain_counts("2021-01-01")
        # Assertions
        assert res == TEST_COUNT_JSON

    def test_get_unknown_counts(self):
        # Setup response
        self.responses.add(
            responses.GET,
            V1_URL + "/clouds/unknownCounts",
            status=200,
            json=TEST_COUNT_JSON,
        )
        # Actual call
        res = self.client.clouds.get_unknown_counts()
        # Assertions
        assert res == TEST_COUNT_JSON
