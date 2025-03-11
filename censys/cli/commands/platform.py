"""Censys Platform CLI commands."""

import argparse
import os
import sys

from rich.prompt import Confirm, Prompt

from censys.cli.utils import console
from censys.common.config import DEFAULT, get_config, write_config


def cli_platform_config(_: argparse.Namespace):  # pragma: no cover
    """Platform config subcommand.

    Args:
        _: Argparse Namespace.
    """
    platform_token_prompt = "Censys Platform Token"
    platform_org_id_prompt = "Censys Organization ID"

    config = get_config()
    platform_token = config.get(DEFAULT, "platform_token", fallback="")
    platform_org_id = config.get(DEFAULT, "platform_org_id", fallback="")

    platform_token_env = os.getenv("CENSYS_PLATFORM_TOKEN")
    platform_org_id_env = os.getenv("CENSYS_ORGANIZATION_ID")

    if platform_token_env is not None:
        console.print(
            "Please note environment variable CENSYS_PLATFORM_TOKEN "
            "will take priority over configured Platform API token."
        )
        platform_token = platform_token_env or platform_token

    if platform_org_id_env is not None:
        console.print(
            "Please note environment variable CENSYS_ORGANIZATION_ID "
            "will take priority over configured Platform Organization ID."
        )
        platform_org_id = platform_org_id_env or platform_org_id

    if platform_token:
        # Only show last 6 characters of the token
        visible_chars = 6
        if len(platform_token) > visible_chars:
            redacted_token = (
                "*" * (len(platform_token) - visible_chars)
                + platform_token[-visible_chars:]
            )
            platform_token_prompt = (
                f"{platform_token_prompt} [cyan]({redacted_token})[/cyan]"
            )

    if platform_org_id:
        redacted_org_id = (
            "*" * (len(platform_org_id) - 4) + platform_org_id[-4:]
            if len(platform_org_id) > 4
            else platform_org_id
        )
        platform_org_id_prompt = (
            f"{platform_org_id_prompt} [cyan]({redacted_org_id})[/cyan]"
        )

    console.print("[bold]Platform API Credentials[/bold]")
    platform_token = (
        Prompt.ask(platform_token_prompt, console=console) or platform_token
    )
    platform_token = platform_token.strip() if platform_token else ""

    if not platform_token:
        console.print("Please enter a valid Platform API token")
        sys.exit(1)

    console.print("\n[bold]Platform Organization ID[/bold]")
    console.print("Required for Platform API access")
    platform_org_id = (
        Prompt.ask(platform_org_id_prompt, console=console) or platform_org_id
    )
    platform_org_id = platform_org_id.strip() if platform_org_id else ""

    if not platform_org_id:
        console.print(
            "[yellow]Warning: Organization ID is required for Platform API access[/yellow]"
        )

    color = Confirm.ask(
        "\nDo you want color output?", default=True, show_default=False, console=console
    )
    config.set(DEFAULT, "color", "auto" if color else "")

    try:
        # Save Platform API token and Organization ID
        config.set(DEFAULT, "platform_token", platform_token)
        config.set(DEFAULT, "platform_org_id", platform_org_id)
        write_config(config)
        console.print("Platform API configuration saved successfully")
        sys.exit(0)
    except PermissionError as e:
        console.print(e)
        console.print(
            "Cannot write config file to directory. "
            + "Please set the `CENSYS_CONFIG_PATH` environmental variable to a writeable location."
        )
        sys.exit(1)


def include(parent_parser: argparse._SubParsersAction, parents: dict):
    """Include this subcommand into the parent parser.

    Args:
        parent_parser (argparse._SubParsersAction): Parent parser.
        parents (dict): Parent arg parsers.
    """
    platform_parser = parent_parser.add_parser(
        "platform",
        description="Censys Platform API Commands",
        help="platform API commands",
    )
    platform_subparsers = platform_parser.add_subparsers()

    # Platform config command
    config_parser = platform_subparsers.add_parser(
        "config",
        description="Configure Censys Platform API Settings",
        help="configure Censys Platform API settings",
    )
    config_parser.set_defaults(func=cli_platform_config)
