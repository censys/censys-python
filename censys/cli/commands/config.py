"""Censys config CLI."""
import argparse
import sys

from rich.prompt import Prompt

from censys.common.config import DEFAULT, get_config, write_config
from censys.common.exceptions import CensysUnauthorizedException
from censys.search.v2.api import CensysSearchAPIv2


def cli_config(_: argparse.Namespace):  # pragma: no cover
    """Config subcommand.

    Args:
        _: Argparse Namespace.
    """
    api_id_prompt = "Censys API ID"
    api_secret_prompt = "Censys API Secret"

    config = get_config()
    api_id = config.get(DEFAULT, "api_id")
    api_secret = config.get(DEFAULT, "api_secret")

    if api_id and api_secret:
        redacted_id = api_id.replace(api_id[:32], 32 * "*")
        redacted_secret = api_secret.replace(api_secret[:28], 28 * "*")
        api_id_prompt = f"{api_id_prompt} [cyan]({redacted_id})[/cyan]"
        api_secret_prompt = f"{api_secret_prompt} [cyan]({redacted_secret})[/cyan]"

    api_id = Prompt.ask(api_id_prompt) or api_id
    api_secret = Prompt.ask(api_secret_prompt) or api_secret

    if not (api_id and api_secret):
        print("Please enter valid credentials")
        sys.exit(1)

    api_id = api_id.strip()
    api_secret = api_secret.strip()

    try:
        client = CensysSearchAPIv2(api_id, api_secret)
        account = client.account()
        email = account.get("email")

        # Assumes that login was successfully
        config.set(DEFAULT, "api_id", api_id)
        config.set(DEFAULT, "api_secret", api_secret)

        write_config(config)
        print(f"\nSuccessfully authenticated for {email}")
        sys.exit(0)
    except CensysUnauthorizedException:
        print("Failed to authenticate")
        sys.exit(1)


def include(parent_parser: argparse._SubParsersAction, parents: dict):
    """Include this subcommand into the parent parser.

    Args:
        parent_parser (argparse._SubParsersAction): Parent parser.
        parents (dict): Parent arg parsers.
    """
    config_parser = parent_parser.add_parser(
        "config",
        description="Configure Censys Search API Settings",
        help="configure Censys search API settings",
    )
    config_parser.set_defaults(func=cli_config)
