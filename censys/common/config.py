"""Interact with the config file."""

import configparser
import contextlib
import os
from pathlib import Path

DEFAULT = "DEFAULT"
HOME_PATH = str(Path.home())
CENSYS_PATH = os.path.join(HOME_PATH, ".config", "censys")
CONFIG_PATH = os.path.join(CENSYS_PATH, "censys.cfg")

default_config = {
    "api_id": "",
    "api_secret": "",
    "asm_api_key": "",
    "color": "auto",
}


def get_config_path() -> str:
    """Returns the path to the config file.

    Returns:
        str: Path to config file.
    """
    alt_path = os.getenv("CENSYS_CONFIG_PATH")
    if alt_path:
        return alt_path
    return CONFIG_PATH


def _restricted_opener(path: str, flags: int) -> int:
    """Opener that creates files readable and writable by the owner only.

    Args:
        path (str): Path to open.
        flags (int): Flags passed by `open()`.

    Returns:
        int: File descriptor.
    """
    return os.open(path, flags, 0o600)


def _try_chmod(path: str, mode: int) -> None:
    """Best-effort permission tightening.

    Files are already created owner-only by `_restricted_opener`, so failing to
    tighten an existing path must never stop the config from being written.

    Args:
        path (str): Path to tighten.
        mode (int): Desired permission bits.
    """
    with contextlib.suppress(OSError):
        os.chmod(path, mode)


def write_config(config: configparser.ConfigParser) -> None:
    """Writes config to file.

    The config file contains API credentials, so the directory and file are
    created owner-only (0700/0600). Existing paths are tightened on a
    best-effort basis; the requested modes are still subject to the umask.

    Args:
        config (configparser.ConfigParser): Configuration to write.

    Raises:
        PermissionError: If the config file is not writable.
    """
    config_path = get_config_path()
    if config_path == CONFIG_PATH:
        if not os.access(HOME_PATH, os.W_OK):
            raise PermissionError(
                "Cannot write to home directory. Please set the `CENSYS_CONFIG_PATH` environmental variable to a writeable location."
            )
        elif not os.path.isdir(CENSYS_PATH):
            os.makedirs(CENSYS_PATH, mode=0o700)
        else:
            _try_chmod(CENSYS_PATH, 0o700)
    if os.path.isfile(config_path):
        _try_chmod(config_path, 0o600)
    with open(config_path, "w", opener=_restricted_opener) as configfile:
        config.write(configfile)


def get_config() -> configparser.ConfigParser:
    """Reads and returns config.

    Returns:
        configparser.ConfigParser: Config for Censys.
    """
    config = configparser.ConfigParser(defaults=default_config, default_section=DEFAULT)
    config_path = get_config_path()
    if os.path.isfile(config_path):
        config.read(config_path)
    return config
