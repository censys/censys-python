import unittest
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest
import responses

from tests.search.v1.test_api import ACCOUNT_JSON
from tests.utils import V1_URL, CensysTestCase

from censys.cli import main as cli_main
from censys.common.config import (
    CENSYS_PATH,
    CONFIG_PATH,
    DEFAULT,
    default_config,
    get_config,
)

os = MagicMock()
os.path = MagicMock()
os.path.isfile = Mock(return_value=False)
os.path.exists = Mock(return_value=False)
os.makedirs = Mock()


def prompt_side_effect(arg, **kwargs):
    if arg == "Censys API ID":
        return CensysTestCase.api_id
    if arg == "Censys API Secret":
        return CensysTestCase.api_secret
    if arg == "Censys API ID [cyan](****************************aaaa)[/cyan]":
        return ""
    if arg == "Censys API Secret [cyan********************************bbbb)[/cyan]":
        return ""
    raise NotImplementedError(f"No prompt handler for {arg}")


def confirm_side_effect(arg, **kwargs):
    if arg == "Do you want color output?":
        return True
    return False


Prompt = MagicMock()
Prompt.ask = Mock(side_effect=prompt_side_effect)

Confirm = MagicMock()
Confirm.ask = Mock(side_effect=confirm_side_effect)

test_config_path = CONFIG_PATH + ".test"


@patch("censys.common.config.CONFIG_PATH", test_config_path)
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data="[DEFAULT]\napi_id =\napi_secret =\nasm_api_key =",
)
@patch("rich.prompt.Prompt.ask", Prompt.ask)
@patch("rich.prompt.Confirm.ask", Confirm.ask)
class CensysConfigCliTest(CensysTestCase):
    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "config",
        ],
    )
    def test_search_config(self, mock_file):
        self.responses.add(
            responses.GET,
            V1_URL + "/account",
            status=200,
            json=ACCOUNT_JSON,
        )

        with pytest.raises(SystemExit, match="0"):
            cli_main()

        # Assert that the config file was read from the right place
        mock_file.assert_called_with(test_config_path, "w")

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "config",
        ],
    )
    def test_search_config_failed(self, mock_file):
        self.responses.add(
            responses.GET,
            V1_URL + "/account",
            status=401,
            json={"error": "Unauthorized"},
        )

        with pytest.raises(SystemExit, match="1"):
            cli_main()

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "config",
        ],
    )
    @patch("censys.common.config.os.path.isdir", Mock(return_value=False))
    @patch("censys.common.config.os.makedirs")
    def test_search_config_makedirs(self, mock_makedirs, mock_file):
        self.responses.add(
            responses.GET,
            V1_URL + "/account",
            status=200,
            json=ACCOUNT_JSON,
        )

        with pytest.raises(SystemExit, match="0"):
            cli_main()

        mock_makedirs.assert_called_with(CENSYS_PATH)

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "config",
        ],
    )
    @patch.dict("censys.common.config.os.environ", {"CENSYS_CONFIG_PATH": "censys.cfg"})
    def test_search_config_custom_config(self, mock_file):
        self.responses.add(
            responses.GET,
            V1_URL + "/account",
            status=200,
            json=ACCOUNT_JSON,
        )

        with pytest.raises(SystemExit, match="0"):
            cli_main()

        # Assert that the config file was read from the right place
        mock_file.assert_called_with("censys.cfg", "w")

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "config",
        ],
    )
    @patch("censys.common.config.os.access", Mock(return_value=False))
    def test_search_config_perm_error(self, mock_file):
        self.responses.add(
            responses.GET,
            V1_URL + "/account",
            status=200,
            json=ACCOUNT_JSON,
        )

        with pytest.raises(SystemExit, match="1"):
            cli_main()


@patch("censys.common.config.CONFIG_PATH", test_config_path)
class CensysConfigTest(unittest.TestCase):
    @patch("censys.common.config.os.path.isfile", os.path.isfile)
    def test_config_default(self):
        config = get_config()
        os.path.isfile.assert_called_with(test_config_path)
        for key, value in default_config.items():
            assert value == config.get(DEFAULT, key)
