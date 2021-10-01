"""Interact with the config file."""
import configparser
import os
from pathlib import Path

DEFAULT = "DEFAULT"

xdg_config_path = os.path.join(str(Path.home()), ".config")
censys_path = os.path.join(xdg_config_path, "censys")
config_path = os.path.join(censys_path, "censys.cfg")

default_config = {
    "api_id": "",
    "api_secret": "",
    "asm_api_key": "",
    "color": "auto",
}


def write_config(config: configparser.ConfigParser) -> None:
    """Writes config to file.

    Args:
        config: Configuration to write.
    """
    with open(config_path, "w") as configfile:
        config.write(configfile)


def get_config() -> configparser.ConfigParser:
    """Reads and returns config.

    Returns:
        configparser.ConfigParser: Config for Censys.
    """
    config = configparser.ConfigParser()
    if not os.path.isdir(xdg_config_path):
        os.mkdir(xdg_config_path)
    if not os.path.isdir(censys_path):
        os.mkdir(censys_path)
    if not os.path.exists(config_path):
        config[DEFAULT] = default_config
        write_config(config)
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
