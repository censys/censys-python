"""Tests for the Censys Platform API base class."""

import unittest
from unittest.mock import mock_open, patch

import pytest
from parameterized import parameterized

from tests.utils import CensysTestCase

from censys.common.exceptions import (
    CensysException,
    CensysNotFoundException,
    CensysRateLimitExceededException,
    CensysUnauthorizedException,
)
from censys.platform.v3.api import CensysPlatformAPIv3

# Test constants
PLATFORM_URL = "https://platform.censys.io/api"

# Exception parameters for testing
PlatformExceptionParams = [
    (401, CensysUnauthorizedException),
    (403, CensysUnauthorizedException),
    (404, CensysNotFoundException),
    (429, CensysRateLimitExceededException),
]


class CensysPlatformAPITests(CensysTestCase):
    """Tests for the base Platform API class."""

    api: CensysPlatformAPIv3

    def setUp(self):
        """Set up test case."""
        self.api = CensysPlatformAPIv3(token="test-token")
        self.api_with_org = CensysPlatformAPIv3(
            token="test-token", organization_id="test-org-id"
        )

    @parameterized.expand(PlatformExceptionParams)
    def test_get_exception_class(self, status_code, exception):
        """Test getting exception class by status code.

        Args:
            status_code: HTTP status code to test.
            exception: Expected exception class.
        """
        res = unittest.mock.Mock()
        res.status_code = status_code
        assert self.api._get_exception_class(res) == exception

    def test_headers(self):
        """Test that proper headers are set."""
        headers = self.api._session.headers
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-token"
        assert headers["Accept"] == "application/json"
        assert headers["Content-Type"] == "application/json"

    def test_headers_with_org_id(self):
        """Test that proper headers are set when organization ID is provided."""
        headers = self.api_with_org._session.headers
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-token"
        assert headers["Accept"] == "application/json"
        assert headers["Content-Type"] == "application/json"
        assert "X-Organization-ID" in headers
        assert headers["X-Organization-ID"] == "test-org-id"

    def test_get_with_organization_id(self):
        """Test that _get method includes organization_id in parameters when provided."""
        with patch.object(self.api_with_org, "_session") as mock_session:
            mock_response = unittest.mock.Mock()
            mock_response.json.return_value = {"status": "ok"}
            mock_session.get.return_value = mock_response

            self.api_with_org._get("test/endpoint")

            # Verify organization_id was added to the query parameters
            args, kwargs = mock_session.get.call_args
            assert "params" in kwargs
            assert kwargs["params"].get("organization_id") == "test-org-id"

    def test_asset_specific_accept_header(self):
        """Test that asset-specific Accept header is set when ASSET_NAME is provided."""

        class TestAssetAPI(CensysPlatformAPIv3):
            """Test API class with asset name."""

            ASSET_NAME = "test-asset"

        # Create a test API with asset name
        test_api = TestAssetAPI(token="test-token")
        headers = test_api._session.headers

        expected_header = "application/vnd.censys.api.v3.test-asset.v1+json"
        assert headers["Accept"] == expected_header


@patch.dict(
    "os.environ", {"CENSYS_API_ID": "", "CENSYS_API_SECRET": "", "CENSYS_API_URL": ""}
)
class CensysPlatformAPIBaseTestsNoEnv(unittest.TestCase):
    """Tests for the Platform API base class without environment variables."""

    @patch("builtins.open", new_callable=mock_open, read_data="[DEFAULT]")
    @patch.object(CensysPlatformAPIv3, "DEFAULT_URL", "")
    def test_no_env(self, mock_file):
        """Test initialization with no environment variables.

        Args:
            mock_file: Mock file object.
        """
        with pytest.raises(CensysException, match="No API url configured"):
            CensysPlatformAPIv3()
