import responses
from parameterized import parameterized
from responses import matchers

from ..utils import CensysTestCase
from .utils import V1_URL, V2_URL
from censys.asm.client import AsmClient
from censys.asm.risks.v2 import Risksv2

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


class Risksv1Tests(CensysTestCase):
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
            V1_URL + f"/risks?pageNumber=1&pageSize=100{params}",
            status=200,
            json=TEST_RISKS_JSON,
        )

        res = list(self.client.risks.get_risks(**kwargs))
        assert res == TEST_RISKS_JSON["data"]


TEST_EVENT_JSON = {
    "delta": "string",
    "id": 0,
    "op": "string",
    "reason": "string",
    "src": "string",
    "srcID": "string",
    "ts": "2022-02-15T20:22:30.262Z",
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


class Risksv2Tests(CensysTestCase):
    api: Risksv2

    def setUp(self):
        super().setUp()
        self.setUpApi(Risksv2(self.api_key))

    @parameterized.expand(
        [
            ({}, ""),
            ({"include_events": True}, "?includeEvents=True"),
            ({"include_events": False}, "?includeEvents=False"),
        ]
    )
    def test_get_risk_instances(self, kwargs, params):
        self.responses.add(
            responses.GET,
            V2_URL + f"/risk-instances{params}",
            status=200,
            json=TEST_RISK_INSTANCES_JSON,
        )

        res = self.api.get_risk_instances(**kwargs)
        assert res == TEST_RISK_INSTANCES_JSON

    def test_patch_risk_instances(self):
        test_patch = {
            "id": 0,
            "categories": ["test-patch"],
        }
        self.responses.add(
            responses.PATCH,
            V2_URL + "/risk-instances",
            status=200,
            json=TEST_PATCH_RISK_INSTANCE_JSON,
            match=[matchers.json_params_matcher(test_patch)],
        )

        res = self.api.patch_risk_instances(test_patch)
        assert res == TEST_PATCH_RISK_INSTANCE_JSON

    def test_search_risk_instances(self):
        test_search = {
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
        self.responses.add(
            responses.POST,
            V2_URL + "/risk-instances/search",
            status=200,
            json=TEST_RISK_TYPE_JSON,
            match=[matchers.json_params_matcher(test_search)],
        )

        res = self.api.search_risk_instances(test_search)
        assert res == TEST_RISK_TYPE_JSON

    @parameterized.expand(
        [
            ({"risk_instance_id": 0}, "0"),
            ({"risk_instance_id": 1, "include_events": True}, "1?includeEvents=True"),
            ({"risk_instance_id": 2, "include_events": False}, "2?includeEvents=False"),
        ]
    )
    def test_get_risk_instance(self, kwargs, params):
        self.responses.add(
            responses.GET,
            V2_URL + f"/risk-instances/{params}",
            status=200,
            json=TEST_RISK_INSTANCE_JSON,
        )

        res = self.api.get_risk_instance(**kwargs)
        assert res == TEST_RISK_INSTANCE_JSON

    def test_patch_risk_instance(self):
        test_risk_id = 0
        test_patch = {
            "id": test_risk_id,
            "categories": ["test-patch"],
        }
        self.responses.add(
            responses.PATCH,
            V2_URL + f"/risk-instances/{test_risk_id}",
            status=200,
            json=TEST_PATCH_RISK_INSTANCE_JSON,
            match=[matchers.json_params_matcher(test_patch)],
        )

        res = self.api.patch_risk_instance(test_risk_id, test_patch)
        assert res == TEST_PATCH_RISK_INSTANCE_JSON

    @parameterized.expand(
        [
            ({}, ""),
            ({"include_events": True}, "?includeEvents=True"),
            ({"include_events": False}, "?includeEvents=False"),
            ({"sort": ["severity", "type:asc"]}, "?sort=severity&sort=type:asc"),
        ]
    )
    def test_get_risk_types(self, kwargs, params):
        self.responses.add(
            responses.GET,
            V2_URL + f"/risk-types{params}",
            status=200,
            json=TEST_RISK_TYPES_JSON,
        )

        res = self.api.get_risk_types(**kwargs)
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
        self.responses.add(
            responses.GET,
            V2_URL + f"/risk-types/{params}",
            status=200,
            json=TEST_RISK_TYPE_JSON,
        )

        res = self.api.get_risk_type(**kwargs)
        assert res == TEST_RISK_TYPE_JSON

    def test_patch_risk_type(self):
        test_patch = {
            "type": TEST_RISK_TYPE,
            "categories": ["test-patch"],
        }
        self.responses.add(
            responses.PATCH,
            V2_URL + f"/risk-types/{TEST_RISK_TYPE}",
            status=200,
            json=TEST_PATCH_RISK_TYPE_JSON,
            match=[matchers.json_params_matcher(test_patch)],
        )

        res = self.api.patch_risk_type(TEST_RISK_TYPE, test_patch)
        assert res == TEST_PATCH_RISK_TYPE_JSON
