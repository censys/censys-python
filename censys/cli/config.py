import sys
from censys.api import CensysSearchAPI
from censys.asm.client import AsmClient
from censys.config import get_config, write_config, DEFAULT
from censys.exceptions import CensysUnauthorizedException


def cli_config(_):  # pragma: no cover
    """
    config subcommand.

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
        api_id_prompt = f"{api_id_prompt} [{redacted_id}]"
        api_secret_prompt = f"{api_secret_prompt} [{redacted_secret}]"

    api_id = input(api_id_prompt + ": ").strip() or api_id
    api_secret = input(api_secret_prompt + ": ").strip() or api_secret

    if not (api_id and api_secret):
        print("Please enter valid credentials")
        sys.exit(1)

    try:
        client = CensysSearchAPI(api_id, api_secret)
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


def cli_asm_config(_):  # pragma: no cover
    """
    config asm subcommand.

    Args:
        _: Argparse Namespace.
    """

    api_key_prompt = "Censys ASM API Key"

    config = get_config()
    api_key = config.get(DEFAULT, "asm_api_key")

    if api_key:
        key_len = len(api_key) - 4
        redacted_api_key = api_key.replace(api_key[:key_len], key_len * "*")
        api_key_prompt = f"{api_key_prompt} [{redacted_api_key}]"

    api_key = input(api_key_prompt + ": ").strip() or api_key

    if not api_key:
        print("Please enter valid credentials")
        sys.exit(1)

    try:
        AsmClient(api_key)

        # Assumes that login was successfully
        config.set(DEFAULT, "asm_api_key", api_key)

        write_config(config)
        print("\nSuccessfully authenticated")
        sys.exit(0)
    except CensysUnauthorizedException:
        print("Failed to authenticate")
        sys.exit(1)
