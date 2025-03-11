"""Tests for the Censys Platform Search API."""

from unittest.mock import patch

from tests.utils import CensysTestCase

from censys.platform.v3.search import CensysSearch

# Test constants
PLATFORM_URL = "https://api.platform.censys.io"
TEST_SEARCH_QUERY = "services.service_name: HTTPS"
TEST_SEARCH_RESPONSE = {"result": {"hits": [{"ip": "1.1.1.1"}]}}
TEST_AGGREGATE_RESPONSE = {"result": {"buckets": [{"key": "HTTPS", "count": 1}]}}


class TestSearch(CensysTestCase):
    """Tests for the Censys Platform Search API."""

    def setUp(self):
        """Set up test case."""
        self.api = CensysSearch(token="test-token")
        self.api_with_org = CensysSearch(
            token="test-token", organization_id="test-org-id"
        )

    def test_init(self):
        """Test initialization."""
        assert self.api._token == "test-token"
        assert self.api.INDEX_NAME == "v3/global/search"

    def test_init_with_org_id(self):
        """Test initialization with organization ID."""
        assert self.api_with_org._token == "test-token"
        assert self.api_with_org.organization_id == "test-org-id"
        assert "X-Organization-ID" in self.api_with_org._session.headers
        assert self.api_with_org._session.headers["X-Organization-ID"] == "test-org-id"

    def test_query(self):
        """Test search query."""
        with patch.object(self.api, "_post") as mock_post:
            self.api.query(TEST_SEARCH_QUERY)
            mock_post.assert_called_with(
                "v3/global/search/query", data={"q": TEST_SEARCH_QUERY, "per_page": 100}
            )

    def test_query_with_org_id(self):
        """Test search query with organization ID."""
        with patch.object(self.api_with_org, "_post") as mock_post:
            self.api_with_org.query(TEST_SEARCH_QUERY)
            mock_post.assert_called_with(
                "v3/global/search/query", data={"q": TEST_SEARCH_QUERY, "per_page": 100}
            )
            # The _post method in the base class will add organization_id to the params

    def test_query_with_params(self):
        """Test search query with parameters."""
        with patch.object(self.api, "_post") as mock_post:
            self.api.query(
                TEST_SEARCH_QUERY,
                per_page=50,
                cursor="nextCursor",
                fields=["ip", "services.port"],
                sort="ip",
            )
            mock_post.assert_called_with(
                "v3/global/search/query",
                data={
                    "q": TEST_SEARCH_QUERY,
                    "per_page": 50,
                    "cursor": "nextCursor",
                    "fields": ["ip", "services.port"],
                    "sort": "ip",
                },
            )

    def test_query_with_params_and_org_id(self):
        """Test search query with parameters and organization ID."""
        with patch.object(self.api_with_org, "_post") as mock_post:
            self.api_with_org.query(
                TEST_SEARCH_QUERY,
                per_page=50,
                cursor="nextCursor",
                fields=["ip", "services.port"],
                sort="ip",
            )
            mock_post.assert_called_with(
                "v3/global/search/query",
                data={
                    "q": TEST_SEARCH_QUERY,
                    "per_page": 50,
                    "cursor": "nextCursor",
                    "fields": ["ip", "services.port"],
                    "sort": "ip",
                },
            )
            # The _post method in the base class will add organization_id to the params

    def test_aggregate(self):
        """Test search aggregate."""
        with patch.object(self.api, "_post") as mock_post:
            self.api.aggregate(TEST_SEARCH_QUERY, "services.service_name")
            mock_post.assert_called_with(
                "v3/global/search/aggregate",
                data={
                    "q": TEST_SEARCH_QUERY,
                    "field": "services.service_name",
                    "num_buckets": 50,
                },
            )

    def test_aggregate_with_org_id(self):
        """Test search aggregate with organization ID."""
        with patch.object(self.api_with_org, "_post") as mock_post:
            self.api_with_org.aggregate(TEST_SEARCH_QUERY, "services.service_name")
            mock_post.assert_called_with(
                "v3/global/search/aggregate",
                data={
                    "q": TEST_SEARCH_QUERY,
                    "field": "services.service_name",
                    "num_buckets": 50,
                },
            )
            # The _post method in the base class will add organization_id to the params
