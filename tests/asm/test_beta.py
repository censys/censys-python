import responses

from ..utils import CensysTestCase
from .utils import BETA_URL
from censys.asm import Beta

TEST_LOGBOOK_DATA = {
    "nextWindowCursor": "string",
    "results": [
        {
            "type": "HOST",
            "logSubType": "ASSOCIATE",
            "ip": "string",
            "id": 0,
            "timestamp": "string",
            "logData": {},
        }
    ],
}
TEST_CLOUD_ASSETS = {
    "addedAssets": ["string"],
    "removedAssets": ["string"],
    "updatedAssets": ["string"],
}
TEST_INPUT_ASSETS = {
    "pageNumber": 0,
    "pageSize": 0,
    "totalPages": 0,
    "totalItems": 0,
    "assets": [{"type": "ASN", "value": "string", "source": "API", "label": "string"}],
}
TEST_ASSET_COUNTS = {
    "environment": "ALL",
    "newAssetsSince": "string",
    "requestCompleteTime": "string",
    "totalCount": 0,
    "totalNewCount": 0,
    "totalCountsBySubEnvironment": [
        {"environment": "string", "totalCount": 0, "totalNewCount": 0}
    ],
}
TEST_HOST_COUNTS_BY_COUNTRY = {
    "environment": "ALL",
    "newAssetsSince": "string",
    "requestCompleteTime": "string",
    "totalCount": 0,
    "totalNewCount": 0,
    "totalCountsBySubEnvironment": [
        {
            "environment": "string",
            "totalCountsByCountry": [
                {
                    "country": "string",
                    "countryCode": "string",
                    "totalCount": 0,
                    "totalNewCount": 0,
                }
            ],
        }
    ],
}
TEST_USER_WORKSPACES = [{"workspace": "string", "roles": ["string"]}]


class BetaUnitTest(CensysTestCase):
    def setUp(self):
        super().setUp()
        self.client = Beta(self.api_key)

    def test_get_logbook_data(self):
        # Setup response
        self.responses.add(
            responses.POST,
            BETA_URL + "/logbook/getLogbookData",
            status=200,
            json=TEST_LOGBOOK_DATA,
        )
        # Actual call
        res = self.client.get_logbook_data(filters={"key": "value"}, cursor="cursor")
        # Assertions
        assert res == TEST_LOGBOOK_DATA

    def test_add_cloud_assets(self):
        # Setup response
        self.responses.add(
            responses.POST,
            BETA_URL + "/cloudConnector/addCloudAssets",
            status=200,
            json=TEST_CLOUD_ASSETS,
        )
        # Actual call
        res = self.client.add_cloud_assets(
            cloud_connector_uid="uid", cloud_assets=[{"key": "value"}]
        )
        # Assertions
        assert res == TEST_CLOUD_ASSETS

    def test_get_input_assets(self):
        # Setup response
        self.responses.add(
            responses.GET,
            BETA_URL + "/assets/inputAssets",
            status=200,
            json=TEST_INPUT_ASSETS,
        )
        # Actual call
        res = self.client.get_input_assets(page_number=1, page_size=10)
        # Assertions
        assert res == TEST_INPUT_ASSETS

    def test_get_asset_counts(self):
        # Setup response
        self.responses.add(
            responses.GET,
            BETA_URL + "/assets/counts",
            status=200,
            json=TEST_ASSET_COUNTS,
        )
        # Actual call
        res = self.client.get_asset_counts(
            since="2021-01-01T00:00:00Z", environment="env", asset_type="type"
        )
        # Assertions
        assert res == TEST_ASSET_COUNTS

    def test_get_host_counts_by_country(self):
        # Setup response
        self.responses.add(
            responses.GET,
            BETA_URL + "/assets/hostCountsByCountry",
            status=200,
            json=TEST_HOST_COUNTS_BY_COUNTRY,
        )
        # Actual call
        res = self.client.get_host_counts_by_country(
            since="2021-01-01T00:00:00Z", environment="env"
        )
        # Assertions
        assert res == TEST_HOST_COUNTS_BY_COUNTRY

    def test_get_user_workspaces(self):
        # Setup response
        self.responses.add(
            responses.GET,
            BETA_URL + "/users/user_uuid/workspaces",
            status=200,
            json=TEST_USER_WORKSPACES,
        )
        # Actual call
        res = self.client.get_user_workspaces(user_uuid="user_uuid")
        # Assertions
        assert res == TEST_USER_WORKSPACES
