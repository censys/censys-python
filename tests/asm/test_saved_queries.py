import responses
from parameterized import parameterized

from ..utils import CensysTestCase
from .utils import BASE_URL
from censys.asm.saved_queries import SavedQueries

SAVED_QUERIES_BASE_PATH = f"{BASE_URL}/inventory/v1/saved-query"

TEST_GET_SAVED_QUERIES_JSON = {
    "results": [
        {
            "createdAt": "2024-01-01T01:00:00.000Z",
            "query": "string",
            "queryId": "string",
            "queryName": "string",
        }
    ],
    "totalResults": 0,
}

TEST_ADD_SAVED_QUERY_JSON = {
    "result": {
        "createdAt": "2024-01-23T04:54:41.679Z",
        "query": "string",
        "queryId": "string",
        "queryName": "string",
    }
}

TEST_GET_SAVED_QUERY_BY_ID_JSON = {
    "result": {
        "createdAt": "2024-01-23T04:55:10.320Z",
        "query": "string",
        "queryId": "string",
        "queryName": "string",
    }
}

TEST_EDIT_SAVED_QUERY_BY_ID_JSON = {
    "result": {
        "createdAt": "2024-01-23T04:55:25.070Z",
        "query": "string",
        "queryId": "string",
        "queryName": "string",
    }
}

TEST_DELETE_SAVED_QUERY_BY_ID_JSON = {}


class SavedQueriesTests(CensysTestCase):
    api: SavedQueries

    def setUp(self):
        super().setUp()
        self.setUpApi(SavedQueries(self.api_key))

    @parameterized.expand(
        [
            (
                {
                    "query_name_prefix": "test-query-name-prefix-1",
                    "page_size": 1,
                    "page": 2,
                    "filter_term": "test-filter-term-1",
                },
                "?queryNamePrefix=test-query-name-prefix-1&pageSize=1&page=2&filterTerm=test-filter-term-1",
            ),
            (
                {
                    "query_name_prefix": "test-query-name-prefix-2",
                    "page_size": 2,
                    "page": 3,
                },
                "?queryNamePrefix=test-query-name-prefix-2&pageSize=2&page=3",
            ),
            (
                {
                    "query_name_prefix": "test-query-name-prefix-3",
                    "page_size": 1,
                    "filter_term": "test-filter-term-3",
                },
                "?queryNamePrefix=test-query-name-prefix-3&pageSize=1&page=1&filterTerm=test-filter-term-3",
            ),
            (
                {
                    "query_name_prefix": "test-query-name-prefix-4",
                    "page": 2,
                    "filter_term": "test-filter-term-4",
                },
                "?queryNamePrefix=test-query-name-prefix-4&pageSize=50&page=2&filterTerm=test-filter-term-4",
            ),
            (
                {"page_size": 1, "page": 2, "filter_term": "test-filter-term-5"},
                "?pageSize=1&page=2&filterTerm=test-filter-term-5",
            ),
            (
                {"query_name_prefix": "test-query-name-prefix-6"},
                "?queryNamePrefix=test-query-name-prefix-6&pageSize=50&page=1",
            ),
            ({}, "?pageSize=50&page=1"),
        ]
    )
    def test_get_saved_queries(self, kwargs, params):
        # Setup response
        self.responses.add(
            responses.GET,
            SAVED_QUERIES_BASE_PATH + params,
            json=TEST_GET_SAVED_QUERIES_JSON,
            status=200,
        )

        # Actual call
        res = self.api.get_saved_queries(**kwargs)

        # Assertions
        assert res == TEST_GET_SAVED_QUERIES_JSON

    @parameterized.expand(
        [
            (
                {"query": "test-query-1", "query_name": "test-query-name-1"},
                {"query": "test-query-1", "queryName": "test-query-name-1"},
            ),
        ]
    )
    def test_add_saved_query(self, kwargs, body):
        # Setup response
        self.responses.add(
            responses.POST,
            SAVED_QUERIES_BASE_PATH,
            status=200,
            json=TEST_ADD_SAVED_QUERY_JSON,
            match=[responses.json_params_matcher(body)],
        )

        # Actual call
        res = self.api.add_saved_query(**kwargs)

        # Assertions
        assert res == TEST_ADD_SAVED_QUERY_JSON

    @parameterized.expand(
        [
            ({"query_id": "test-query-id-1"}, "/test-query-id-1"),
        ]
    )
    def test_get_saved_query_by_id(self, kwargs, path):
        # Setup response
        self.responses.add(
            responses.GET,
            SAVED_QUERIES_BASE_PATH + path,
            status=200,
            json=TEST_GET_SAVED_QUERY_BY_ID_JSON,
        )

        # Actual call
        res = self.api.get_saved_query_by_id(**kwargs)

        # Assertions
        assert res == TEST_GET_SAVED_QUERY_BY_ID_JSON

    @parameterized.expand(
        [
            (
                {
                    "query_id": "test-query-id-1",
                    "query": "test-query-1",
                    "query_name": "test-query-name-1",
                },
                {"query": "test-query-1", "queryName": "test-query-name-1"},
                "/test-query-id-1",
            ),
        ]
    )
    def test_edit_saved_query_by_id(self, kwargs, body, path):
        # Setup response
        self.responses.add(
            responses.PUT,
            SAVED_QUERIES_BASE_PATH + path,
            status=200,
            json=TEST_EDIT_SAVED_QUERY_BY_ID_JSON,
            match=[responses.json_params_matcher(body)],
        )

        # Actual call
        res = self.api.edit_saved_query_by_id(**kwargs)

        # Assertions
        assert res == TEST_EDIT_SAVED_QUERY_BY_ID_JSON

    @parameterized.expand(
        [
            ({"query_id": "test-query-id-1"}, "/test-query-id-1"),
        ]
    )
    def test_delete_saved_query_by_id(self, kwargs, path):
        # Setup response
        self.responses.add(
            responses.DELETE,
            SAVED_QUERIES_BASE_PATH + path,
            status=200,
            json=TEST_DELETE_SAVED_QUERY_BY_ID_JSON,
        )

        # Actual call
        res = self.api.delete_saved_query_by_id(**kwargs)

        # Assertions
        assert res == TEST_DELETE_SAVED_QUERY_BY_ID_JSON
