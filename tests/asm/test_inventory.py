import responses
from parameterized import parameterized

from ..utils import CensysTestCase
from .utils import BASE_URL, WORKSPACE_ID
from censys.asm.inventory import InventorySearch

INVENTORY_BASE_PATH = f"{BASE_URL}/inventory/v1"
INVENTORY_SEARCH_PATH = INVENTORY_BASE_PATH
INVENTORY_AGGREGATE_PATH = f"{INVENTORY_BASE_PATH}/aggregate"
INVENTORY_FIELDS_PATH = f"{INVENTORY_BASE_PATH}/fields"

TEST_INVENTORY_SEARCH_JSON = {
    "totalHits": 0,
    "nextCursor": "string",
    "previousCursor": "string",
    "queryDurationMillis": 0,
    "hits": [{}],
}
TEST_INVENTORY_AGGREGATE_JSON = {
    "workspaces": ["string"],
    "query": "string",
    "aggregation": {
        "term": {"field": "string", "numberOfBuckets": 0},
        "rareTerm": {"field": "string", "maxCount": 0},
        "nested": {"path": "string"},
        "reverseNested": {"path": "string"},
        "filter": {"query": "string"},
        "cardinality": {"field": "string"},
    },
}
TEST_INVENTORY_FIELDS_JSON = {
    "fields": [
        {"path": "string", "type": "string", "description": "string", "repeated": True}
    ]
}


class InventoryTests(CensysTestCase):
    api: InventorySearch

    def setUp(self):
        super().setUp()
        self.setUpApi(InventorySearch(self.api_key))

    @parameterized.expand(
        [
            (
                {
                    "query": "test",
                    "page_size": 50,
                    "cursor": "test",
                    "sort": ["test"],
                    "fields": ["test"],
                },
                "?workspaces=test-workspace-id&query=test&pageSize=50&cursor=test&sort=test&fields=test",
            ),
            (
                {
                    "workspaces": ["1", "2"],
                    "query": "test",
                },
                "?workspaces=test-workspace-id&query=test&pageSize=50",
            ),
        ]
    )
    def test_search(self, kwargs, params):
        mock_request = self.mocker.patch("censys.asm.api.CensysAsmAPI.get_workspace_id")
        mock_request.return_value = WORKSPACE_ID

        # Setup response
        self.responses.add(
            responses.GET,
            INVENTORY_SEARCH_PATH + params,
            status=200,
            json=TEST_INVENTORY_SEARCH_JSON,
        )

        # Actual call
        res = self.api.search(**kwargs)

        # Assertions
        assert res == TEST_INVENTORY_SEARCH_JSON

    @parameterized.expand(
        [
            (
                {
                    "workspaces": ["1", "2"],
                    "query": "test",
                    "aggregation": {
                        "field": "test",
                        "size": 50,
                        "sort": "test",
                        "order": "test",
                    },
                },
            ),
        ]
    )
    def test_aggregate(self, kwargs):
        # Setup response
        self.responses.add(
            responses.POST,
            INVENTORY_AGGREGATE_PATH,
            status=200,
            json=TEST_INVENTORY_AGGREGATE_JSON,
            match=[responses.matchers.json_params_matcher(kwargs)],
        )

        # Actual call
        res = self.api.aggregate(**kwargs)

        # Assertions
        assert res == TEST_INVENTORY_AGGREGATE_JSON

    @parameterized.expand(
        [
            (
                {
                    "fields": ["host.services.name", "host.services.port"],
                },
                "?fields=host.services.name&fields=host.services.port",
            ),
        ]
    )
    def test_fields(self, kwargs, params):
        # Setup response
        self.responses.add(
            responses.GET,
            INVENTORY_FIELDS_PATH + params,
            status=200,
            json=TEST_INVENTORY_FIELDS_JSON,
        )

        # Actual call
        res = self.api.fields(**kwargs)

        # Assertions
        assert res == TEST_INVENTORY_FIELDS_JSON
