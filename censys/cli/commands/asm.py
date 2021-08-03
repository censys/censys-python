import argparse
import json
import sys

from rich.prompt import Prompt

from censys.asm.seeds import SEED_TYPES
from censys.common.config import DEFAULT, get_config, write_config
from censys.common.exceptions import CensysUnauthorizedException


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


def cli_add_seeds(args: argparse.Namespace):
    """Add seed subcommand.

    Args:
        args (Namespace): Argparse Namespace.
    """
    if args.input_file:
        if args.input_file == "-":
            data = sys.stdin.read()
        else:
            with open(args.input_file, "r") as f:
                data = f.read()
    else:
        data = args.json
    try:
        seeds = json.loads(data)
    except json.decoder.JSONDecodeError as e:
        print(f"Invalid json {e}")
        sys.exit(1)

    seeds_to_add = []
    for seed in seeds:
        if isinstance(seed, dict):
            if "type" not in seed:
                seed["type"] = args.type
        elif isinstance(seed, str):
            seed = {"value": seed, "type": args.type}
        else:
            print(f"Invalid seed {seed}")
        seeds_to_add.append(seed)

    print(seeds_to_add)


def include(parent_parser: argparse._SubParsersAction, parents: dict) -> None:
    """Include this subcommand into the parent parser."""
    asm_parser = parent_parser.add_parser(
        "asm", description="Interact with the Censys ASM API", help="interact with ASM"
    )
    asm_subparser = asm_parser.add_subparsers()

    # Add config command
    config_parser = asm_subparser.add_parser(
        "config",
        description="Configure Censys ASM API Settings",
        help="configure Censys ASM API settings",
    )
    config_parser.set_defaults(func=cli_asm_config)

    # Add seed command
    add_parser = asm_subparser.add_parser(
        "add-seeds",
        description="Add seeds to ASM",
        help="add seeds",
    )
    add_parser.add_argument(
        "--type",
        help="type of the seeds (default: %(default)s)",
        choices=SEED_TYPES,
        default="IP_ADDRESS",
    )
    seeds_group = add_parser.add_mutually_exclusive_group(required=True)
    seeds_group.add_argument(
        "--input-file",
        "-i",
        help="input file name containing valid json seeds (use - for stdin)",
        type=str,
    )
    seeds_group.add_argument(
        "--json", "-j", help="input string containing valid json seeds", type=str
    )
    add_parser.set_defaults(func=cli_add_seeds)
