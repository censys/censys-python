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

TEST_CONFIG_PATH = CONFIG_PATH + ".test"


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


class CensysConfigCliTest(CensysTestCase):
    def setUp(self):
        super().setUp()
        self.mocker.patch("censys.common.config.CONFIG_PATH", TEST_CONFIG_PATH)
        self.mock_open = self.mocker.patch(
            "builtins.open",
            new_callable=self.mocker.mock_open,
            read_data="[DEFAULT]\napi_id =\napi_secret =\nasm_api_key =",
        )
        mock_prompt = self.mocker.patch(
            "rich.prompt.Prompt.ask", side_effect=prompt_side_effect
        )
        mock_confirm = self.mocker.patch(
            "rich.prompt.Confirm.ask", side_effect=confirm_side_effect
        )

    def test_search_config(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "config",
            ]
        )
        self.responses.add(
            responses.GET,
            V1_URL + "/account",
            status=200,
            json=ACCOUNT_JSON,
        )

        with pytest.raises(SystemExit, match="0"):
            cli_main()

        # Assert that the config file was read from the right place
        self.mock_open.assert_called_with(TEST_CONFIG_PATH, "w")

    def test_search_config_failed(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "config",
            ]
        )
        self.responses.add(
            responses.GET,
            V1_URL + "/account",
            status=401,
            json={"error": "Unauthorized"},
        )

        # Actual call/error raising
        with pytest.raises(SystemExit, match="1"):
            cli_main()

    def test_search_config_makedirs(self):
        self.patch_args(
            [
                "censys",
                "config",
            ]
        )
        self.mocker.patch("censys.common.config.os.path.isdir", return_value=False)
        mock_makedirs = self.mocker.patch("censys.common.config.os.makedirs")

        self.responses.add(
            responses.GET,
            V1_URL + "/account",
            status=200,
            json=ACCOUNT_JSON,
        )

        with pytest.raises(SystemExit, match="0"):
            cli_main()

        mock_makedirs.assert_called_with(CENSYS_PATH)

    def test_config_default(self):
        mock_isfile = self.mocker.patch(
            "censys.common.config.os.path.isfile", return_value=True
        )
        config = get_config()
        mock_isfile.return_value = False
        mock_isfile.assert_called_with(TEST_CONFIG_PATH)
        self.mock_open.assert_called_once()
        for key, value in default_config.items():
            assert value == config.get(DEFAULT, key)

    def test_search_config_custom_config(self):
        self.patch_args(
            [
                "censys",
                "config",
            ]
        )
        self.mocker.patch.dict(
            "censys.common.config.os.environ", {"CENSYS_CONFIG_PATH": "censys.cfg"}
        )

        self.responses.add(
            responses.GET,
            V1_URL + "/account",
            status=200,
            json=ACCOUNT_JSON,
        )

        with pytest.raises(SystemExit, match="0"):
            cli_main()

        # Assert that the config file was read from the right place
        self.mock_open.assert_called_with("censys.cfg", "w")

    def test_search_config_perm_error(self):
        self.patch_args(
            [
                "censys",
                "config",
            ]
        )
        self.mocker.patch("censys.common.config.os.access", return_value=False)
        self.responses.add(
            responses.GET,
            V1_URL + "/account",
            status=200,
            json=ACCOUNT_JSON,
        )

        with pytest.raises(SystemExit, match="1"):
            cli_main()
