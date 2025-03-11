"""Tests for the Censys Platform Hosts API."""

import datetime
from unittest.mock import patch

import responses

from tests.utils import CensysTestCase

from censys.platform.v3.hosts import CensysHosts

# Test constants
TEST_HOST = "1.1.1.1"
TEST_HOSTS = ["1.1.1.1", "8.8.8.8"]
PLATFORM_URL = "https://api.platform.censys.io"
TEST_HOST_RESPONSE = {"host": {"name": TEST_HOST}}
TEST_BULK_RESPONSE = {"result": [{"host": {"name": host}} for host in TEST_HOSTS]}
TEST_TIMELINE_RESPONSE = {"result": [{"timestamp": "2023-01-01T00:00:00Z"}]}


class TestHosts(CensysTestCase):
    """Tests for the Platform Hosts API."""

    def setUp(self):
        """Set up test case."""
        self.api = CensysHosts(token="test-token")
        self.api_with_org = CensysHosts(
            token="test-token", organization_id="test-org-id"
        )

    def test_init(self):
        """Test initialization."""
        assert self.api._token == "test-token"
        assert self.api.INDEX_NAME == "v3/global/asset/host"
        assert self.api.ASSET_NAME == "host"

    def test_init_with_org_id(self):
        """Test initialization with organization ID."""
        assert self.api_with_org._token == "test-token"
        assert self.api_with_org.organization_id == "test-org-id"
        assert "X-Organization-ID" in self.api_with_org._session.headers
        assert self.api_with_org._session.headers["X-Organization-ID"] == "test-org-id"

    def test_view(self):
        """Test view method."""
        with patch.object(self.api, "_get") as mock_get:
            self.api.view("1.1.1.1")
            mock_get.assert_called_with("v3/global/asset/host/1.1.1.1", params={})

    def test_view_with_org_id(self):
        """Test view method with organization ID."""
        with patch.object(self.api_with_org, "_get") as mock_get:
            self.api_with_org.view("1.1.1.1")
            mock_get.assert_called_with("v3/global/asset/host/1.1.1.1", params={})
            # The _get method in the base class will add organization_id to the params

    def test_bulk_view(self):
        """Test bulk_view method."""
        with patch.object(self.api, "_get") as mock_get:
            self.api.bulk_view(["1.1.1.1", "8.8.8.8"])
            mock_get.assert_called_with(
                "v3/global/asset/host", params={"host_ids": ["1.1.1.1", "8.8.8.8"]}
            )

    def test_bulk_view_with_org_id(self):
        """Test bulk_view method with organization ID."""
        with patch.object(self.api_with_org, "_get") as mock_get:
            self.api_with_org.bulk_view(["1.1.1.1", "8.8.8.8"])
            mock_get.assert_called_with(
                "v3/global/asset/host", params={"host_ids": ["1.1.1.1", "8.8.8.8"]}
            )
            # The _get method in the base class will add organization_id to the params

    def test_timeline(self):
        """Test timeline method."""
        with patch.object(self.api, "_get") as mock_get:
            self.api.timeline("1.1.1.1")
            mock_get.assert_called_with(
                "v3/global/asset/host/1.1.1.1/timeline", params={}
            )

    def test_timeline_with_org_id(self):
        """Test timeline method with organization ID."""
        with patch.object(self.api_with_org, "_get") as mock_get:
            self.api_with_org.timeline("1.1.1.1")
            mock_get.assert_called_with(
                "v3/global/asset/host/1.1.1.1/timeline", params={}
            )
            # The _get method in the base class will add organization_id to the params

    @responses.activate
    def test_view_at_time(self):
        """Test viewing host details at a specific time."""
        test_date = datetime.datetime(2023, 1, 1)
        responses.add(
            responses.GET,
            f"{PLATFORM_URL}/v3/global/asset/host/{TEST_HOST}",
            json=TEST_HOST_RESPONSE,
            status=200,
        )
        res = self.api.view(TEST_HOST, at_time=test_date)
        assert res == TEST_HOST_RESPONSE
        assert "at_time" in responses.calls[0].request.url
        assert "2023-01-01" in responses.calls[0].request.url

    @responses.activate
    def test_timeline_with_dates(self):
        """Test viewing host timeline with date parameters."""
        start_date = datetime.datetime(2023, 1, 1)
        end_date = datetime.datetime(2023, 1, 2)
        responses.add(
            responses.GET,
            f"{PLATFORM_URL}/v3/global/asset/host/{TEST_HOST}/timeline",
            json=TEST_TIMELINE_RESPONSE,
            status=200,
        )
        res = self.api.timeline(TEST_HOST, start_time=start_date, end_time=end_date)
        assert res == TEST_TIMELINE_RESPONSE
        assert "start_time" in responses.calls[0].request.url
        assert "end_time" in responses.calls[0].request.url
        assert "2023-01-01" in responses.calls[0].request.url
        assert "2023-01-02" in responses.calls[0].request.url
