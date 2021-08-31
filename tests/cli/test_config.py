import unittest
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest
import responses

from tests.search.v1.test_api import ACCOUNT_JSON
from tests.utils import V1_ENDPOINT_ON_V2_URL, CensysTestCase

from censys.cli import main as cli_main
from censys.common.config import DEFAULT, censys_path, config_path, get_config

os = MagicMock()
os.path = MagicMock()
os.path.isdir = Mock(return_value=False)
os.path.exists = Mock(return_value=False)
os.mkdir = Mock()


def prompt_side_effect(arg):
    if arg == "Censys API ID":
        return CensysTestCase.api_id
    if arg == "Censys API Secret":
        return CensysTestCase.api_secret
    if arg == "Censys API ID [cyan](****************************aaaa)[/cyan]":
        return ""
    if arg == "Censys API Secret [cyan********************************bbbb)[/cyan]":
        return ""
    raise NotImplementedError(f"No prompt handler for {arg}")


Prompt = MagicMock()
Prompt.ask = Mock(side_effect=prompt_side_effect)

test_config_path = config_path + ".test"


@patch("censys.common.config.config_path", test_config_path)
class CensysConfigCliTest(CensysTestCase):
    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "config",
        ],
    )
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="[DEFAULT]\napi_id =\napi_secret =\nasm_api_key =",
    )
    @patch("censys.common.config.write_config")
    @patch("rich.prompt.Prompt.ask", Prompt.ask)
    def test_search_config(self, mock_write_config, mock_file):
        self.responses.add(
            responses.GET,
            V1_ENDPOINT_ON_V2_URL + "/account",
            status=200,
            json=ACCOUNT_JSON,
        )

        with pytest.raises(SystemExit, match="0"):
            cli_main()

        # Assert that the config file was read from the right place
        mock_file.assert_called_with(test_config_path, "w")

        # Assert the config was updated correctly
        config = get_config()
        config.set(DEFAULT, "api_id", self.api_id)
        config.set(DEFAULT, "api_secret", self.api_secret)
        mock_write_config.assert_called_with(config)

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "config",
        ],
    )
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="[DEFAULT]\napi_id =\napi_secret =\nasm_api_key =",
    )
    @patch("rich.prompt.Prompt.ask", Prompt.ask)
    def test_search_config_failed(self, mock_file):
        self.responses.add(
            responses.GET,
            V1_ENDPOINT_ON_V2_URL + "/account",
            status=401,
            json={"error": "Unauthorized"},
        )

        with pytest.raises(SystemExit, match="1"):
            cli_main()


@patch("censys.common.config.config_path", test_config_path)
class CensysConfigTest(unittest.TestCase):
    @patch("censys.common.config.os.path", os.path)
    @patch("censys.common.config.os.mkdir", os.mkdir)
    @patch("builtins.open", new_callable=mock_open)
    def test_write_default(self, mock_file):
        get_config()
        os.path.isdir.assert_called_with(censys_path)
        os.mkdir.assert_called_with(censys_path)
        os.path.exists.assert_called_with(test_config_path)
        mock_file.assert_called_with(test_config_path, "w")
