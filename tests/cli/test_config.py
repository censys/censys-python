import os
import stat
from unittest.mock import patch

import pytest
import responses
from pytest_mock import MockerFixture

from censys.cli import main as cli_main
from censys.common.config import (
    CENSYS_PATH,
    CONFIG_PATH,
    DEFAULT,
    _restricted_opener,
    default_config,
    get_config,
    write_config,
)
from tests.search.v1.test_api import ACCOUNT_JSON
from tests.utils import V1_URL, CensysTestCase

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
    return arg == "Do you want color output?"


class CensysConfigCliTest(CensysTestCase):
    @pytest.fixture(autouse=True)
    def _config_setup(self, mocker: MockerFixture):
        mocker.patch("censys.common.config.CONFIG_PATH", TEST_CONFIG_PATH)
        self.mock_open = mocker.patch(
            "builtins.open",
            new_callable=mocker.mock_open,
            read_data="[DEFAULT]\napi_id =\napi_secret =\nasm_api_key =",
        )
        mocker.patch("rich.prompt.Prompt.ask", side_effect=prompt_side_effect)
        mocker.patch("rich.prompt.Confirm.ask", side_effect=confirm_side_effect)
        self.mock_chmod = mocker.patch("censys.common.config._try_chmod")

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
        self.mock_open.assert_called_with(TEST_CONFIG_PATH, "w", opener=_restricted_opener)

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

        mock_makedirs.assert_called_with(CENSYS_PATH, mode=0o700)

    def test_config_default(self):
        mock_isfile = self.mocker.patch("censys.common.config.os.path.isfile", return_value=True)
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
        self.mocker.patch.dict("censys.common.config.os.environ", {"CENSYS_CONFIG_PATH": "censys.cfg"})

        self.responses.add(
            responses.GET,
            V1_URL + "/account",
            status=200,
            json=ACCOUNT_JSON,
        )

        with pytest.raises(SystemExit, match="0"):
            cli_main()

        # Assert that the config file was read from the right place
        self.mock_open.assert_called_with("censys.cfg", "w", opener=_restricted_opener)

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


@pytest.fixture
def home_config(tmp_path, mocker, monkeypatch):
    """Points the default config location at a throwaway home directory."""
    monkeypatch.delenv("CENSYS_CONFIG_PATH", raising=False)
    censys_path = tmp_path / ".config" / "censys"
    config_path = censys_path / "censys.cfg"
    mocker.patch("censys.common.config.HOME_PATH", str(tmp_path))
    mocker.patch("censys.common.config.CENSYS_PATH", str(censys_path))
    mocker.patch("censys.common.config.CONFIG_PATH", str(config_path))
    return censys_path, config_path


def test_write_config_creates_and_rewrites(home_config):
    censys_path, config_path = home_config

    # First write creates the directory and the file
    write_config(get_config())
    assert censys_path.is_dir()
    assert config_path.is_file()

    # Second write takes the existing-directory and existing-file branches
    write_config(get_config())
    assert get_config().get(DEFAULT, "color") == "auto"


def test_write_config_survives_unchmodable_path(home_config):
    # A path we may not chmod must not stop the config from being written:
    # root-owned config dirs in containers, a non-owned CENSYS_CONFIG_PATH, and
    # mounts that reject chmod outright (NFS, CIFS, WSL DrvFs without metadata).
    _, config_path = home_config

    write_config(get_config())

    with patch(
        "censys.common.config.os.chmod",
        side_effect=PermissionError(1, "Operation not permitted"),
    ):
        write_config(get_config())

    assert config_path.is_file()


@pytest.mark.skipif(os.name != "posix", reason="POSIX file permissions only")
def test_write_config_restricts_permissions(home_config):
    censys_path, config_path = home_config
    old_umask = os.umask(0o022)
    try:
        write_config(get_config())

        assert stat.S_IMODE(os.stat(censys_path).st_mode) & 0o077 == 0
        assert stat.S_IMODE(os.stat(config_path).st_mode) & 0o077 == 0

        # Pre-existing loose permissions are tightened on rewrite
        os.chmod(censys_path, 0o755)
        os.chmod(config_path, 0o644)
        write_config(get_config())

        assert stat.S_IMODE(os.stat(censys_path).st_mode) & 0o077 == 0
        assert stat.S_IMODE(os.stat(config_path).st_mode) & 0o077 == 0
    finally:
        os.umask(old_umask)


@pytest.mark.skipif(os.name != "posix", reason="POSIX file permissions only")
def test_write_config_keeps_permissions_when_chmod_fails(home_config):
    _, config_path = home_config

    write_config(get_config())

    with patch(
        "censys.common.config.os.chmod",
        side_effect=PermissionError(1, "Operation not permitted"),
    ):
        write_config(get_config())

    assert stat.S_IMODE(os.stat(config_path).st_mode) & 0o077 == 0
