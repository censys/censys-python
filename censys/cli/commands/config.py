"""Censys config CLI."""
import argparse
import sys

from rich.prompt import Prompt

from censys.common.config import DEFAULT, get_config, write_config
from censys.common.exceptions import CensysUnauthorizedException
from censys.search.v1.api import CensysSearchAPIv1


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
        client = CensysSearchAPIv1(api_id, api_secret)
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


def cli_asm_config(_: argparse.Namespace):  # pragma: no cover
    """Config asm subcommand.

    Args:
        _: Argparse Namespace.
    """
    api_key_prompt = "Censys ASM API Key"

    config = get_config()
    api_key = config.get(DEFAULT, "asm_api_key")

    if api_key:
        key_len = len(api_key) - 4
        redacted_api_key = api_key.replace(api_key[:key_len], key_len * "*")
        api_key_prompt = f"{api_key_prompt} [cyan]({redacted_api_key})[/cyan]"

    api_key = Prompt.ask(api_key_prompt) or api_key

    if not api_key:
        print("Please enter valid credentials")
        sys.exit(1)

    try:
        # Assumes that login was successfully
        config.set(DEFAULT, "asm_api_key", api_key)

        write_config(config)
        print("\nSuccessfully configured credentials")
        sys.exit(0)
    except CensysUnauthorizedException:
        print("Failed to authenticate")
        sys.exit(1)
