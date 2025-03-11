"""Tests for the Censys Platform Client."""

import unittest
from unittest.mock import patch

from censys.platform import CensysPlatformClient
from censys.platform.v3 import (
    CensysCertificates,
    CensysHosts,
    CensysSearch,
    CensysWebProperties,
)


class CensysPlatformClientTests(unittest.TestCase):
    """Tests for the CensysPlatformClient class."""

    def setUp(self):
        """Set up test case."""
        self.client = CensysPlatformClient(
            token="test-token", organization_id="test-org-id"
        )

    def test_client_initialization(self):
        """Test that client initializes properly with all API instances."""
        # Verify client has all expected API instances
        assert isinstance(self.client.hosts, CensysHosts)
        assert isinstance(self.client.certificates, CensysCertificates)
        assert isinstance(self.client.webproperties, CensysWebProperties)
        assert isinstance(self.client.search, CensysSearch)

    def test_credential_propagation(self):
        """Test that credentials are properly propagated to all API instances."""
        # Check that organization_id was passed to all instances
        assert self.client.hosts.organization_id == "test-org-id"
        assert self.client.certificates.organization_id == "test-org-id"
        assert self.client.webproperties.organization_id == "test-org-id"
        assert self.client.search.organization_id == "test-org-id"

        # Check that token was passed to all instances (indirectly by checking session headers)
        assert (
            self.client.hosts._session.headers["Authorization"] == "Bearer test-token"
        )
        assert (
            self.client.certificates._session.headers["Authorization"]
            == "Bearer test-token"
        )
        assert (
            self.client.webproperties._session.headers["Authorization"]
            == "Bearer test-token"
        )
        assert (
            self.client.search._session.headers["Authorization"] == "Bearer test-token"
        )

    @patch("censys.platform.v3.search.CensysSearch.query")
    def test_search_delegation(self, mock_query):
        """Test that search query calls are properly delegated to the appropriate API instances.

        Args:
            mock_query: Mock object for the CensysSearch.query method.
        """
        # Setup mock return value
        mock_query.return_value = {"result": {"total": 1, "hits": [{"ip": "8.8.8.8"}]}}

        # Call query through client
        result = self.client.search.query("host.services: (port = 22)")

        # Verify query was called with correct parameters
        mock_query.assert_called_once_with("host.services: (port = 22)")
        assert result == {"result": {"total": 1, "hits": [{"ip": "8.8.8.8"}]}}
