"""Censys config."""
import configparser
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field

HOME_PATH = Path.home()
# CENSYS_PATH = HOME_PATH / ".config" / "censys"
CENSYS_PATH = HOME_PATH / ".censys"  # TODO: Remove, this is for development
CONFIG_PATH = CENSYS_PATH / "censys.cfg"


class Profile(BaseModel):
    """Base class for profiles."""

    profile_type: Literal["search", "asm"] = Field(
        ..., description="Type of profile.", alias="type"
    )
    profile_name: str = Field(..., description="Profile name.", alias="name")
    base_url: str = Field(..., description="Base URL for the API.")
    timeout: int = Field(..., description="Timeout for the API.", gt=0)
    max_retries: int = Field(
        ..., description="Max number of retries for the API.", gt=0
    )
    user_agent: Optional[str] = Field(
        description="User agent to append to the User-Agent header.", default=None
    )
    proxies: Optional[dict] = Field(description="Proxies for the API.", default=None)
    cookies: Optional[dict] = Field(description="Cookies for the API.", default=None)
    color: bool = Field(description="Whether to use color in the output.", default=True)


class SearchProfile(Profile):
    """Search profile."""

    profile_type: Literal["search"] = Field(
        ..., description="Type of profile.", alias="type"
    )
    base_url: str = Field(
        description="Base URL for the API.",
        default="https://search.censys.io/api",
        alias="search_base_url",
    )
    api_id: str = Field(..., description="Search API ID.")
    api_secret: str = Field(..., description="Search API secret.")


class AsmProfile(Profile):
    """ASM profile."""

    profile_type: Literal["asm"] = Field(
        ..., description="Type of profile.", alias="type"
    )
    base_url: str = Field(
        description="Base URL for the API.",
        default="https://app.censys.io/api",
        alias="asm_base_url",
    )
    api_key: str = Field(..., description="ASM API key.", alias="asm_api_key")


class Config(BaseModel):
    """Censys config."""

    search_profiles: Optional[dict[str, SearchProfile]] = Field(
        description="Search profiles.", default=None
    )
    asm_profiles: Optional[dict[str, AsmProfile]] = Field(
        description="ASM profiles.", default=None
    )


def load_config() -> Config:
    """Load the config.

    Returns:
        The config.

    Raises:
        ValueError: If the profile type is invalid.
    """
    # Read the config file
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    # Create the config object
    search_profiles = {}
    asm_profiles = {}
    for section in config.sections():
        profile_type = config[section].get("type")
        if profile_type == "search":
            search_profiles[section] = SearchProfile(**config[section])
        elif profile_type == "asm":
            asm_profiles[section] = AsmProfile(**config[section])
        else:
            raise ValueError(f"Invalid profile type: {profile_type}")
    return Config(search_profiles=search_profiles, asm_profiles=asm_profiles)


def save_config(config: Config) -> None:
    """Save the config.

    Args:
        config: The config.
    """
    # Create the config parser
    config_parser = configparser.ConfigParser()

    # Add the profiles
    for profile_name, profile in config.search_profiles.items():
        config_parser[profile_name] = profile.dict()
    for profile_name, profile in config.asm_profiles.items():
        config_parser[profile_name] = profile.dict()

    # Write the config file
    CENSYS_PATH.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as config_file:
        config_parser.write(config_file)
