"""End-to-end tests for the Censys Platform API.

These tests require valid Platform credentials and make actual API calls.
They should only be run manually and not in CI environments.
"""
import configparser
import os

import pytest

from tests.utils import CensysTestCase

from censys.common.config import DEFAULT, get_config
from censys.platform.v3.search import CensysSearch, ResultPaginator

# Mark the entire module as "e2e" tests
pytestmark = pytest.mark.e2e


def is_config_valid() -> bool:
    """Check if Censys Platform credentials are properly configured.

    Returns:
        bool: True if both CENSYS_PLATFORM_TOKEN and CENSYS_ORGANIZATION_ID are found,
              either as environment variables or in the configuration file.
    """
    # Check environment variables first
    token = os.environ.get("CENSYS_PLATFORM_TOKEN")
    org_id = os.environ.get("CENSYS_ORGANIZATION_ID")

    if token and org_id:
        return True

    # If not in environment variables, check config file
    try:
        config = get_config()
        token = config.get(DEFAULT, "platform_token", fallback=None)
        org_id = config.get(DEFAULT, "platform_org_id", fallback=None)
        return bool(token and org_id)
    except (configparser.Error, FileNotFoundError):
        return False


class TestPlatformEndToEnd(CensysTestCase):
    """End-to-end tests for the Platform Search API."""

    def test_live_search(self, request):
        """Test live search against the Censys Platform API.

        This test makes real API calls to the Censys Platform API and will
        count against your quota when run with the --run-e2e flag.

        Args:
            request: Pytest request fixture to access config options
        """
        # Skip this test unless --run-e2e flag is provided
        run_e2e = request.config.getoption("--run-e2e", default=False)
        if not run_e2e:
            pytest.skip("Test requires --run-e2e flag to run")

        # Also check if we have valid credentials
        if not is_config_valid():
            pytest.skip(
                "No Censys Platform credentials found. Run 'censys platform config' to configure."
            )

        # Get credentials from environment variables or config file
        token = os.environ.get("CENSYS_PLATFORM_TOKEN")
        org_id = os.environ.get("CENSYS_ORGANIZATION_ID")

        if not token or not org_id:
            # If environment variables are not set, try config file
            config = get_config()
            token = config.get(DEFAULT, "platform_token", fallback=None)
            org_id = config.get(DEFAULT, "platform_org_id", fallback=None)

        # Initialize client with real credentials
        client = CensysSearch(token=token, organization_id=org_id)

        # Test simple query
        query_result = client.query("services.port:443", per_page=5)
        assert "result" in query_result
        assert "hits" in query_result["result"]

        # Test pagination
        paginator = ResultPaginator(client, "services.port:443", per_page=2)

        # Get first page
        page1 = paginator.get_page()
        assert len(page1) > 0

        # Get second page if it exists
        if paginator.has_next_page():
            page2 = paginator.get_page()
            assert len(page2) > 0

        # Test get_all_results
        all_results = paginator.get_all_results(max_results=5)
        assert len(all_results) > 0
        assert len(all_results) <= 5  # We limited to 5 results
