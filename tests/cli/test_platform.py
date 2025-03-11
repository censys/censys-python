"""Tests for CLI platform commands."""

import os
from unittest.mock import MagicMock, patch

from censys.cli.commands.platform import get_platform_client
from censys.common.config import DEFAULT


@patch("censys.cli.commands.platform.get_config")
@patch("censys.cli.commands.platform.console")
@patch("censys.cli.commands.platform.CensysPlatformClient")
def test_get_platform_client_with_env_vars(mock_client, mock_console, mock_get_config):
    """Test get_platform_client with environment variables.

    Args:
        mock_client: Mock of the CensysPlatformClient.
        mock_console: Mock of the console object.
        mock_get_config: Mock of the get_config function.
    """
    # Mock environment variables
    with patch.dict(
        os.environ,
        {
            "CENSYS_PLATFORM_TOKEN": "test-token",
            "CENSYS_ORGANIZATION_ID": "test-org-id",
        },
    ):
        # Mock config
        mock_config = MagicMock()
        mock_get_config.return_value = mock_config

        # Call the function
        client = get_platform_client()

        # Assertions
        mock_client.assert_called_once_with(
            token="test-token", organization_id="test-org-id"
        )
        assert client == mock_client.return_value


@patch("censys.cli.commands.platform.get_config")
@patch("censys.cli.commands.platform.console")
@patch("censys.cli.commands.platform.CensysPlatformClient")
def test_get_platform_client_with_config(mock_client, mock_console, mock_get_config):
    """Test get_platform_client with config values.

    Args:
        mock_client: Mock of the CensysPlatformClient.
        mock_console: Mock of the console object.
        mock_get_config: Mock of the get_config function.
    """
    # Clear environment variables
    with patch.dict(
        os.environ,
        {"CENSYS_PLATFORM_TOKEN": "", "CENSYS_ORGANIZATION_ID": ""},
        clear=True,
    ):
        # Mock config
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda section, key, fallback=None: {
            (DEFAULT, "platform_token"): "config-token",
            (DEFAULT, "platform_org_id"): "config-org-id",
        }.get((section, key), fallback)
        mock_get_config.return_value = mock_config

        # Call the function
        client = get_platform_client()

        # Assertions
        mock_client.assert_called_once_with(
            token="config-token", organization_id="config-org-id"
        )
        assert client == mock_client.return_value


@patch("censys.cli.commands.platform.get_config")
@patch("censys.cli.commands.platform.console")
@patch("censys.cli.commands.platform.sys.exit")
def test_get_platform_client_missing_token(mock_exit, mock_console, mock_get_config):
    """Test get_platform_client with missing token.

    Args:
        mock_exit: Mock of sys.exit function.
        mock_console: Mock of the console object.
        mock_get_config: Mock of the get_config function.
    """
    # Clear environment variables
    with patch.dict(
        os.environ,
        {"CENSYS_PLATFORM_TOKEN": "", "CENSYS_ORGANIZATION_ID": "test-org-id"},
        clear=True,
    ):
        # Mock config
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda section, key, fallback=None: {
            (DEFAULT, "platform_token"): None,
            (DEFAULT, "platform_org_id"): "config-org-id",
        }.get((section, key), fallback)
        mock_get_config.return_value = mock_config

        # Call the function
        get_platform_client()

        # Assertions
        mock_console.print.assert_called_once()
        mock_exit.assert_called_once_with(1)


@patch("censys.cli.commands.platform.get_config")
@patch("censys.cli.commands.platform.console")
@patch("censys.cli.commands.platform.sys.exit")
def test_get_platform_client_missing_org_id(mock_exit, mock_console, mock_get_config):
    """Test get_platform_client with missing organization ID.

    Args:
        mock_exit: Mock of sys.exit function.
        mock_console: Mock of the console object.
        mock_get_config: Mock of the get_config function.
    """
    # Clear environment variables
    with patch.dict(
        os.environ,
        {"CENSYS_PLATFORM_TOKEN": "test-token", "CENSYS_ORGANIZATION_ID": ""},
        clear=True,
    ):
        # Mock config
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda section, key, fallback=None: {
            (DEFAULT, "platform_token"): "config-token",
            (DEFAULT, "platform_org_id"): None,
        }.get((section, key), fallback)
        mock_get_config.return_value = mock_config

        # Call the function
        get_platform_client()

        # Assertions
        mock_console.print.assert_called_once()
        mock_exit.assert_called_once_with(1)
