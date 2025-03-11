"""Censys config CLI."""

import argparse
import os
import sys

from rich.prompt import Confirm, Prompt

from censys.cli.utils import console
from censys.common.config import DEFAULT, get_config, write_config
from censys.common.exceptions import CensysUnauthorizedException
from censys.search.v2.api import CensysSearchAPIv2


def cli_config(_: argparse.Namespace):  # pragma: no cover
    """Config subcommand.

    Args:
        _: Argparse Namespace.
    """
    config = get_config()
    api_id = os.getenv("CENSYS_API_ID") or config.get(DEFAULT, "api_id")
    api_secret = os.getenv("CENSYS_API_SECRET") or config.get(DEFAULT, "api_secret")

    if os.getenv("CENSYS_API_ID") or os.getenv("CENSYS_API_SECRET"):
        console.print(
            "Note: Environment variables (CENSYS_API_ID & CENSYS_API_SECRET) "
            "take priority over configured credentials."
        )

    def redact(value, length):
        return value.replace(value[:length], length * "*") if value else value

    api_id_prompt = f"Censys API ID [cyan]({redact(api_id, 32)})[/cyan]" if api_id else "Censys API ID"
    api_secret_prompt = f"Censys API Secret [cyan]({redact(api_secret, 28)})[/cyan]" if api_secret else "Censys API Secret"

    api_id = (Prompt.ask(api_id_prompt, console=console) or api_id).strip()
    api_secret = (Prompt.ask(api_secret_prompt, console=console) or api_secret).strip()

    if not (api_id and api_secret):
        console.print("Please enter valid credentials")
        sys.exit(1)

    color = Confirm.ask("Do you want color output?", default=True, show_default=False, console=console)
    config.set(DEFAULT, "color", "auto" if color else "")

    try:
        client = CensysSearchAPIv2(api_id, api_secret)
        email = client.account().get("email")
        console.print(f"\nSuccessfully authenticated for {email}")

        config.set(DEFAULT, "api_id", api_id)
        config.set(DEFAULT, "api_secret", api_secret)
        write_config(config)
        sys.exit(0)
    except CensysUnauthorizedException:
        console.print("Failed to authenticate")
        sys.exit(1)
    except PermissionError as e:
        console.print(e)
        console.print(
            "Cannot write config file to directory. "
            "Please set the `CENSYS_CONFIG_PATH` environmental variable to a writeable location."
        )
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