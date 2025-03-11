"""Tests for the Censys Platform WebProperty API."""

import datetime
from unittest.mock import patch

from tests.utils import CensysTestCase

from censys.platform.v3.webproperties import CensysWebProperties

# Test constants
PLATFORM_URL = "https://api.platform.censys.io"
TEST_WEBPROPERTY = "example.com:443"
TEST_WEBPROPERTIES = ["example.com:443", "example.org:443"]
TEST_WEBPROPERTY_RESPONSE = {"webproperty": {"name": TEST_WEBPROPERTY}}
TEST_BULK_RESPONSE = {
    "result": [{"webproperty": {"name": wp}} for wp in TEST_WEBPROPERTIES]
}


class TestWebProperties(CensysTestCase):
    """Tests for the Censys Platform WebProperty API."""

    def setUp(self):
        """Set up test case."""
        self.api = CensysWebProperties(token="test-token")
        self.api_with_org = CensysWebProperties(
            token="test-token", organization_id="test-org-id"
        )

    def test_init(self):
        """Test initialization."""
        assert self.api._token == "test-token"
        assert self.api.INDEX_NAME == "v3/global/asset/webproperty"
        assert self.api.ASSET_NAME == "webproperty"

    def test_init_with_org_id(self):
        """Test initialization with organization ID."""
        assert self.api_with_org._token == "test-token"
        assert self.api_with_org.organization_id == "test-org-id"
        assert "X-Organization-ID" in self.api_with_org._session.headers
        assert self.api_with_org._session.headers["X-Organization-ID"] == "test-org-id"

    def test_view(self):
        """Test view method."""
        with patch.object(self.api, "_get") as mock_get:
            self.api.view(TEST_WEBPROPERTY)
            mock_get.assert_called_with(
                f"v3/global/asset/webproperty/{TEST_WEBPROPERTY}", params={}
            )

    def test_view_with_org_id(self):
        """Test view method with organization ID."""
        with patch.object(self.api_with_org, "_get") as mock_get:
            self.api_with_org.view(TEST_WEBPROPERTY)
            mock_get.assert_called_with(
                f"v3/global/asset/webproperty/{TEST_WEBPROPERTY}", params={}
            )
            # The _get method in the base class will add organization_id to the params

    def test_view_at_time(self):
        """Test viewing webproperty details at a specific time."""
        test_date = datetime.datetime(2023, 1, 1)
        with patch.object(self.api, "_get") as mock_get:
            self.api.view(TEST_WEBPROPERTY, at_time=test_date)
            mock_get.assert_called_with(
                f"v3/global/asset/webproperty/{TEST_WEBPROPERTY}",
                params={"at_time": "2023-01-01T00:00:00.000000Z"},
            )

    def test_view_at_time_with_org_id(self):
        """Test viewing webproperty details at a specific time with organization ID."""
        test_date = datetime.datetime(2023, 1, 1)
        with patch.object(self.api_with_org, "_get") as mock_get:
            self.api_with_org.view(TEST_WEBPROPERTY, at_time=test_date)
            mock_get.assert_called_with(
                f"v3/global/asset/webproperty/{TEST_WEBPROPERTY}",
                params={"at_time": "2023-01-01T00:00:00.000000Z"},
            )
            # The _get method in the base class will add organization_id to the params

    def test_bulk_view(self):
        """Test bulk_view method."""
        with patch.object(self.api, "_get") as mock_get:
            self.api.bulk_view(TEST_WEBPROPERTIES)
            mock_get.assert_called_with(
                "v3/global/asset/webproperty",
                params={"webproperty_ids": TEST_WEBPROPERTIES},
            )

    def test_bulk_view_with_org_id(self):
        """Test bulk_view method with organization ID."""
        with patch.object(self.api_with_org, "_get") as mock_get:
            self.api_with_org.bulk_view(TEST_WEBPROPERTIES)
            mock_get.assert_called_with(
                "v3/global/asset/webproperty",
                params={"webproperty_ids": TEST_WEBPROPERTIES},
            )
            # The _get method in the base class will add organization_id to the params
