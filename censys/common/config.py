"""Interact with the config file."""
import configparser
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


def write_config(config: configparser.ConfigParser) -> None:
    """Writes config to file.

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
            os.makedirs(CENSYS_PATH)
    with open(config_path, "w") as configfile:
        config.write(configfile)


def get_config() -> configparser.ConfigParser:
    """Reads and returns config.

    Returns:
        configparser.ConfigParser: Config for Censys.
    """
    config = configparser.ConfigParser()
    config_path = get_config_path()
    if not os.path.isfile(config_path):
        config[DEFAULT] = default_config
    else:
        config.read(config_path)
    check_config(config)
    return config


def check_config(config: configparser.ConfigParser):
    """Checks config against default config for fields.

    Args:
        config (configparser.ConfigParser): Configuration to write.
    """
    for key in default_config:
        try:
            config.get(DEFAULT, key)
        except configparser.NoOptionError:
            config.set(DEFAULT, key, default_config.get(key))
