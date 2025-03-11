"""Tests for the Censys Platform Certificate API."""

from unittest.mock import patch

from tests.utils import CensysTestCase

from censys.platform.v3.certificates import CensysCertificates

# Test constants
PLATFORM_URL = "https://api.platform.censys.io"
TEST_CERTIFICATE = "a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1"
TEST_CERTIFICATES = [
    "a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1",
    "b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2",
]
TEST_CERTIFICATE_RESPONSE = {"certificate": {"fingerprint_sha256": TEST_CERTIFICATE}}
TEST_BULK_RESPONSE = {
    "result": [
        {"certificate": {"fingerprint_sha256": cert}} for cert in TEST_CERTIFICATES
    ]
}


class TestCertificates(CensysTestCase):
    """Tests for the Censys Platform Certificate API."""

    def setUp(self):
        """Set up test case."""
        self.api = CensysCertificates(token="test-token")
        self.api_with_org = CensysCertificates(
            token="test-token", organization_id="test-org-id"
        )

    def test_init(self):
        """Test initialization."""
        assert self.api._token == "test-token"
        assert self.api.INDEX_NAME == "v3/global/asset/certificate"
        assert self.api.ASSET_NAME == "certificate"

    def test_init_with_org_id(self):
        """Test initialization with organization ID."""
        assert self.api_with_org._token == "test-token"
        assert self.api_with_org.organization_id == "test-org-id"
        assert "X-Organization-ID" in self.api_with_org._session.headers
        assert self.api_with_org._session.headers["X-Organization-ID"] == "test-org-id"

    def test_view(self):
        """Test view method."""
        with patch.object(self.api, "_get") as mock_get:
            self.api.view(TEST_CERTIFICATE)
            mock_get.assert_called_with(
                f"v3/global/asset/certificate/{TEST_CERTIFICATE}"
            )

    def test_view_with_org_id(self):
        """Test view method with organization ID."""
        with patch.object(self.api_with_org, "_get") as mock_get:
            self.api_with_org.view(TEST_CERTIFICATE)
            mock_get.assert_called_with(
                f"v3/global/asset/certificate/{TEST_CERTIFICATE}"
            )
            # The _get method in the base class will add organization_id to the params

    def test_bulk_view(self):
        """Test bulk_view method."""
        with patch.object(self.api, "_get") as mock_get:
            self.api.bulk_view(TEST_CERTIFICATES)
            mock_get.assert_called_with(
                "v3/global/asset/certificate",
                params={"certificate_ids": TEST_CERTIFICATES},
            )

    def test_bulk_view_with_org_id(self):
        """Test bulk_view method with organization ID."""
        with patch.object(self.api_with_org, "_get") as mock_get:
            self.api_with_org.bulk_view(TEST_CERTIFICATES)
            mock_get.assert_called_with(
                "v3/global/asset/certificate",
                params={"certificate_ids": TEST_CERTIFICATES},
            )
            # The _get method in the base class will add organization_id to the params
