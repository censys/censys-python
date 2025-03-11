"""Tests for error handling in the CensysPlatformAPIv3 class."""

import configparser
from unittest.mock import patch

import pytest

from censys.platform.v3.api import CensysPlatformAPIv3


def test_init_with_api_id_warning():
    """Test initialization with deprecated api_id and api_secret parameters."""
    with pytest.warns(DeprecationWarning):
        CensysPlatformAPIv3(
            token="test-token", api_id="test-id", api_secret="test-secret"
        )


@patch("censys.platform.v3.api.get_config")
def test_init_missing_token(mock_get_config):
    """Test initialization with missing token.

    Args:
        mock_get_config: Mock of the get_config function.
    """
    # Mock the config to return empty values
    config = configparser.ConfigParser()
    config["DEFAULT"]["platform_token"] = ""
    config["DEFAULT"]["platform_org_id"] = "test-org"
    mock_get_config.return_value = config

    # Test the ValueError is raised
    with pytest.raises(
        ValueError, match="Personal Access Token is required for Platform API."
    ):
        CensysPlatformAPIv3(token=None, organization_id=None)


@patch("censys.platform.v3.api.get_config")
def test_init_missing_organization_id(mock_get_config):
    """Test initialization with missing organization_id when authenticating.

    Args:
        mock_get_config: Mock of the get_config function.
    """
    # Mock the config to return empty values
    config = configparser.ConfigParser()
    config["DEFAULT"]["platform_token"] = "test-token"
    config["DEFAULT"]["platform_org_id"] = ""
    mock_get_config.return_value = config

    # Test the ValueError is raised
    with pytest.raises(
        ValueError, match="Organization ID is required for Platform API."
    ):
        CensysPlatformAPIv3(token=None, organization_id=None)


@patch("censys.common.base.CensysAPIBase._get")
def test_get_with_organization_id_and_args(mock_base_get):
    """Test _get with organization_id and existing args.

    Args:
        mock_base_get: Mock of the base _get method.
    """
    api = CensysPlatformAPIv3(token="test-token", organization_id="test-org")
    api._get("endpoint", {"arg1": "value1"})
    mock_base_get.assert_called_with(
        "endpoint", {"arg1": "value1", "organization_id": "test-org"}
    )


@patch("censys.common.base.CensysAPIBase._get")
def test_get_with_organization_id_no_args(mock_base_get):
    """Test _get with organization_id and no args.

    Args:
        mock_base_get: Mock of the base _get method.
    """
    api = CensysPlatformAPIv3(token="test-token", organization_id="test-org")
    api._get("endpoint")
    mock_base_get.assert_called_with("endpoint", {"organization_id": "test-org"})


@patch("censys.common.base.CensysAPIBase._get")
def test_view_with_params(mock_base_get):
    """Test view with params.

    Args:
        mock_base_get: Mock of the base _get method.
    """
    api = CensysPlatformAPIv3(token="test-token", organization_id="test-org")
    api.INDEX_NAME = "test-index"
    api.view("resource-id", params={"param1": "value1"})

    # The actual implementation passes params to _get
    mock_base_get.assert_called_with(
        f"{api.INDEX_NAME}/resource-id",
        {"organization_id": "test-org"},
        params={"param1": "value1"},
    )
