import responses
from parameterized import parameterized
from responses import matchers

from ..utils import CensysTestCase
from .utils import V2_URL
from censys.asm.risks import Risks

TEST_EVENT_JSON = {
    "delta": "string",
    "id": 0,
    "op": "string",
    "reason": "string",
    "src": "string",
    "srcID": "string",
    "ts": "2022-02-15T20:22:30.262Z",
}
TEST_RISK_EVENTS_JSON = {
    "total": 1,
    "next": "eyJhZnRlcklEIjo3NzQwLCJsaW1pdCI6MTAwfQ==",
    "events": [TEST_EVENT_JSON],
    "endOfEvents": True,
}
TEST_RISK_INSTANCE_JSON = {
    "id": 0,
    "events": [TEST_EVENT_JSON],
    "metadata": [{"src": "system"}],
}
TEST_RISK_INSTANCES_JSON = {
    "risks": [TEST_RISK_INSTANCE_JSON],
}
TEST_PATCH_RISK_INSTANCE_JSON = {
    "categoriesChanges": 0,
    "changes": 0,
    "metadataAdded": 0,
    "metadataRemoved": 0,
    "severityChanges": 0,
    "skips": 0,
    "userStatusChanges": 0,
}
TEST_RISK_TYPE = "service.authentication.http_weak_auth.http_weak_auth_encrypted"
TEST_RISK_TYPE_JSON = {
    "config": "string",
    "contextType": "string",
    "defaultCategories": [["string"]],
    "defaultSeverity": "low",
    "description": "string",
    "enabled": True,
    "events": [TEST_EVENT_JSON],
    "lastDisableReason": "string",
    "lastSeverityChangeReason": "string",
    "lastUpdatedAt": "2022-02-15T20:22:30.262Z",
    "name": "string",
    "recommendedSeverity": "low",
    "remediations": ["string"],
    "riskCount": 0,
    "subjectType": "string",
    "type": "string",
}
TEST_RISK_TYPES_JSON = {
    "type": [TEST_RISK_TYPE_JSON],
}
TEST_PATCH_RISK_TYPE_JSON = {
    "changes": 0,
    "configChanges": 0,
    "defaultCategoriesChanges": 0,
    "defaultSeverityChanges": 0,
    "enabledChanges": 0,
}


class RisksTests(CensysTestCase):
    api: Risks

    def setUp(self):
        super().setUp()
        self.setUpApi(Risks(self.api_key))

    @parameterized.expand(
        [
            ({}, ""),
            (
                {"start": "2023-12-14T03:27:00Z", "end": "2022-03-18T09:18:54Z"},
                "?start=2023-12-14T03:27:00Z&end=2022-03-18T09:18:54Z",
            ),
            ({"after_id": 489, "limit": 100}, "?afterID=489&limit=100"),
            (
                {"cursor": "eyJhZnRlcklEIjo3NzQwLCJsaW1pdCI6MTAwfQ=="},
                "?cursor=eyJhZnRlcklEIjo3NzQwLCJsaW1pdCI6MTAwfQ==",
            ),
        ]
    )
    def test_get_risk_events(self, kwargs, params):
        # Setup response
        self.responses.add(
            responses.GET,
            V2_URL + f"/risk-events{params}",
            status=200,
            json=TEST_RISK_EVENTS_JSON,
        )
        # Actual call
        res = self.api.get_risk_events(**kwargs)
        # Assertions
        assert res == TEST_RISK_EVENTS_JSON

    @parameterized.expand(
        [
            ({}, ""),
            ({"include_events": True}, "?includeEvents=True"),
            ({"include_events": False}, "?includeEvents=False"),
        ]
    )
    def test_get_risk_instances(self, kwargs, params):
        # Setup response
        self.responses.add(
            responses.GET,
            V2_URL + f"/risk-instances{params}",
            status=200,
            json=TEST_RISK_INSTANCES_JSON,
        )
        # Actual call
        res = self.api.get_risk_instances(**kwargs)
        # Assertions
        assert res == TEST_RISK_INSTANCES_JSON

    def test_patch_risk_instances(self):
        # Mock
        mock_patch = self.mocker.patch.dict(
            {
                "id": 0,
                "categories": ["test-patch"],
            }
        )
        self.responses.add(
            responses.PATCH,
            V2_URL + "/risk-instances",
            status=200,
            json=TEST_PATCH_RISK_INSTANCE_JSON,
            match=[matchers.json_params_matcher(mock_patch)],
        )
        # Actual call
        res = self.api.patch_risk_instances(mock_patch)
        # Assertions
        assert res == TEST_PATCH_RISK_INSTANCE_JSON

    def test_search_risk_instances(self):
        # Mock
        mock_search = self.mocker.patch.dict(
            {
                "fields": ["id", "context", "type", "metadata", "events"],
                "limit": 1000,
                "page": 1,
                "query": {
                    "field": "firstComputedAt",
                    "operator": "=",
                    "value": "2022-02-15T17:46:10.328Z",
                },
                "sort": ["severity", {"context.type": "asc"}],
            }
        )
        self.responses.add(
            responses.POST,
            V2_URL + "/risk-instances/search",
            status=200,
            json=TEST_RISK_TYPE_JSON,
            match=[matchers.json_params_matcher(mock_search)],
        )
        # Actual call
        res = self.api.search_risk_instances(mock_search)
        # Assertions
        assert res == TEST_RISK_TYPE_JSON

    @parameterized.expand(
        [
            ({"risk_instance_id": 0}, "0"),
            ({"risk_instance_id": 1, "include_events": True}, "1?includeEvents=True"),
            ({"risk_instance_id": 2, "include_events": False}, "2?includeEvents=False"),
        ]
    )
    def test_get_risk_instance(self, kwargs, params):
        # Setup response
        self.responses.add(
            responses.GET,
            V2_URL + f"/risk-instances/{params}",
            status=200,
            json=TEST_RISK_INSTANCE_JSON,
        )
        # Actual call
        res = self.api.get_risk_instance(**kwargs)
        # Assertions
        assert res == TEST_RISK_INSTANCE_JSON

    def test_patch_risk_instance(self):
        # Mock
        mock_risk_id = 0
        mock_patch = self.mocker.patch.dict(
            {
                "id": mock_risk_id,
                "categories": ["mock-patch"],
            }
        )
        self.responses.add(
            responses.PATCH,
            V2_URL + f"/risk-instances/{mock_risk_id}",
            status=200,
            json=TEST_PATCH_RISK_INSTANCE_JSON,
            match=[matchers.json_params_matcher(mock_patch)],
        )
        # Actual call
        res = self.api.patch_risk_instance(mock_risk_id, mock_patch)
        # Assertions
        assert res == TEST_PATCH_RISK_INSTANCE_JSON

    @parameterized.expand(
        [
            ({}, ""),
            ({"include_events": True}, "?includeEvents=True"),
            ({"include_events": False}, "?includeEvents=False"),
            ({"sort": ["severity", "type:asc"]}, "?sort=severity&sort=type:asc"),
            ({"page": 1, "limit": 10000}, "?page=1&limit=10000"),
            ({"page": 10}, "?page=10"),
        ]
    )
    def test_get_risk_types(self, kwargs, params):
        # Setup response
        self.responses.add(
            responses.GET,
            V2_URL + f"/risk-types{params}",
            status=200,
            json=TEST_RISK_TYPES_JSON,
        )
        # Actual call
        res = self.api.get_risk_types(**kwargs)
        # Assertions
        assert res == TEST_RISK_TYPES_JSON

    @parameterized.expand(
        [
            ({"risk_type": TEST_RISK_TYPE}, TEST_RISK_TYPE),
            (
                {"risk_type": TEST_RISK_TYPE, "include_events": True},
                TEST_RISK_TYPE + "?includeEvents=True",
            ),
            (
                {"risk_type": TEST_RISK_TYPE, "include_events": False},
                TEST_RISK_TYPE + "?includeEvents=False",
            ),
        ]
    )
    def test_get_risk_type(self, kwargs, params):
        # Setup respnonse
        self.responses.add(
            responses.GET,
            V2_URL + f"/risk-types/{params}",
            status=200,
            json=TEST_RISK_TYPE_JSON,
        )
        # Actual call
        res = self.api.get_risk_type(**kwargs)
        # Assertions
        assert res == TEST_RISK_TYPE_JSON

    def test_patch_risk_type(self):
        # Mock
        mock_patch = self.mocker.patch.dict(
            {
                "type": TEST_RISK_TYPE,
                "categories": ["mock-patch"],
            }
        )
        self.responses.add(
            responses.PATCH,
            V2_URL + f"/risk-types/{TEST_RISK_TYPE}",
            status=200,
            json=TEST_PATCH_RISK_TYPE_JSON,
            match=[matchers.json_params_matcher(mock_patch)],
        )
        # Actual call
        res = self.api.patch_risk_type(TEST_RISK_TYPE, mock_patch)
        # Assertions
        assert res == TEST_PATCH_RISK_TYPE_JSON
