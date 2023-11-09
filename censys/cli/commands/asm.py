"""Censys ASM CLI."""
import argparse
import concurrent.futures
import csv
import json
import sys
import threading
from typing import Dict, List, Union
from xml.etree import ElementTree

from rich.progress import Progress, TaskID
from rich.prompt import Confirm, Prompt

from censys.asm.seeds import SEED_TYPES, Seeds
from censys.cli.utils import console
from censys.common.config import DEFAULT, get_config, write_config
from censys.common.exceptions import (
    CensysSeedNotFoundException,
    CensysUnauthorizedException,
)


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

    api_key = Prompt.ask(api_key_prompt, console=console) or api_key

    if not api_key:
        console.print("Please enter valid credentials")
        sys.exit(1)

    color = Confirm.ask(
        "Do you want color output?", default=True, show_default=False, console=console
    )
    config.set(DEFAULT, "color", "auto" if color else "")

    try:
        # Assumes that login was successfully
        config.set(DEFAULT, "asm_api_key", api_key)

        write_config(config)
        console.print("\nSuccessfully configured credentials")
        sys.exit(0)
    except CensysUnauthorizedException:
        console.print("Failed to authenticate")
        sys.exit(1)


def get_seeds_from_xml(file: str) -> List[Dict[str, str]]:
    """Get seeds from nmap xml.

    Args:
        file (str): Nmap xml file.

    Returns:
        List[Dict[str, str]]: List of seeds.
    """
    tree = ElementTree.parse(file)
    root = tree.getroot()
    ips = set()
    domains = set()
    for element in root.findall("host"):
        address_element = element.find("address")
        hostnames_element = element.find("hostnames")
        if address_element is not None and address_element.get("addrtype") == "ipv4":
            ip_address = address_element.get("addr")
            if ip_address:
                ips.add(ip_address)
        if hostnames_element is not None:
            hostname_elements = hostnames_element.findall("hostname")
            for hostname_element in hostname_elements:
                hostname_type = hostname_element.get("type")
                if hostname_type != "user":
                    continue
                hostname = hostname_element.get("name")
                if hostname:
                    domains.add(hostname)
    return [{"value": ip, "type": "IP_ADDRESS"} for ip in ips] + [
        {"value": domain, "type": "DOMAIN_NAME"} for domain in domains
    ]


def get_seeds_from_params(
    args: argparse.Namespace, command_name: str
) -> List[Dict[str, Union[str, int]]]:
    """Get seeds from params.

    Args:
        args (Namespace): Argparse Namespace.
        command_name (str): The name of the command getting the seeds to be processed.

    Returns:
        List[Dict[str, str]]: List of seeds.
    """
    is_csv = args.csv
    if args.input_file or args.json:
        json_data = None
        if args.input_file:
            if args.input_file == "-":
                file = sys.stdin
            else:
                if not args.csv and args.input_file.endswith(".csv"):
                    is_csv = True
                file = open(args.input_file)  # noqa: SIM115

            if is_csv:
                seeds = []
                csv_reader = csv.DictReader(file, delimiter=",")
                if csv_reader.fieldnames:
                    # Lowercase the field names
                    csv_reader.fieldnames = [
                        string.lower() for string in csv_reader.fieldnames
                    ]
                for row in csv_reader:
                    seeds.append(row)
            else:
                json_data = file.read()
        else:
            json_data = args.json

        if json_data:
            try:
                seeds = json.loads(json_data)
            except json.decoder.JSONDecodeError as e:
                console.print(f"Invalid json {e}")
                sys.exit(1)
    elif args.nmap_xml:
        try:
            seeds = get_seeds_from_xml(args.nmap_xml)
        except ElementTree.ParseError as e:
            console.print(f"Invalid xml {e}")
            sys.exit(1)

    seeds_to_add = []
    for seed in seeds:
        if isinstance(seed, str):
            seed = {"value": seed}

        if not isinstance(seed, dict):
            console.print(f"Invalid seed {seed}")
            sys.exit(1)

        if command_name != "delete-seeds" and "type" not in seed:
            seed["type"] = args.default_type

        if (
            command_name != "replace-labeled-seeds"
            and "label" not in seed
            and "label" in args
        ):
            seed["label"] = args.label

        # The back end is really picky about sending extra fields, so we'll prune out anything it won't like.
        # This makes it possible to output to CSV, edit, and then pipe the same CSV back into add-seeds, where
        # we will strip the id, source, createdOn, and any other junk that might be there
        #
        valid_params = ["type", "value"]
        if command_name == "add-seeds":
            valid_params.append("label")
        elif command_name == "delete-seeds" and "value" not in seed:
            valid_params.append("id")
        filtered_seeds = {key: seed[key] for key in seed if key in valid_params}
        seeds_to_add.append(filtered_seeds)

    return seeds_to_add


def console_clear_line():
    """Clear previous line in console."""
    sys.stdout.write("\033[F")  # Move the cursor to the previous line
    sys.stdout.write("\033[K")  # Clear the line


def cli_add_seeds(args: argparse.Namespace):
    """Add seed subcommand.

    Args:
        args (Namespace): Argparse Namespace.
    """
    seeds_to_add = get_seeds_from_params(args, "add-seeds")

    s = Seeds(args.api_key)
    to_add_count = len(seeds_to_add)
    res = s.add_seeds(seeds_to_add)
    added_seeds = res["addedSeeds"]
    added_count = len(added_seeds)
    if not added_count:
        console.print("No seeds were added. (Run with -v to get more info)")
        if not args.verbose:
            sys.exit(1)
    else:
        console.print(f"Added {added_count} seeds.")
    if added_count < to_add_count:
        console.print(f"Seeds not added: {to_add_count - added_count}")
        if args.verbose:  # pragma: no cover
            console.print(
                "The following seed(s) were not able to be added as they already exist or are reserved."
            )
            for seed in seeds_to_add:
                if not any(s for s in added_seeds if seed["value"] == s["value"]):
                    console.print(f"{seed}")


def cli_delete_seeds(args: argparse.Namespace):
    """Delete seeds subcommand.

    Args:
        args (Namespace): Argparse Namespace.
    """
    seeds_to_delete = get_seeds_from_params(args, "delete-seeds")
    s = Seeds(args.api_key)

    # Get all seeds into a dict indexed by value (for later lookups)
    console.print("Getting seeds...")
    seeds = s.get_seeds()
    console_clear_line()

    seeds_dict_indexed_by_value = {}
    for seed in seeds:
        seeds_dict_indexed_by_value[seed["value"]] = seed

    seed_ids_to_delete = []
    seed_ids_not_found = []
    for seed_to_delete in seeds_to_delete:
        if seed_id := seed_to_delete.get("id"):
            seed_ids_to_delete.append(seed_id)
        elif seed_value := seed_to_delete.get("value"):
            # value may not be in current seeds - can't delete
            if seed_value in seeds_dict_indexed_by_value:
                seed_ids_to_delete.append(seeds_dict_indexed_by_value[seed_value]["id"])
            else:
                seed_ids_not_found.append(seed_value)
        else:
            console.print("Error, no seed id or value for seed.")

    if len(seed_ids_to_delete) == 0:
        console.print("No seeds to delete.")
        sys.exit(0)

    seed_ids_deleted = []

    # Create a lock to protect shared variables
    lock = threading.Lock()

    def delete_seed(seed_id: int, progress: Progress, task_id: TaskID):
        try:
            s.delete_seed_by_id(seed_id)
            with lock:
                nonlocal seed_ids_deleted
                seed_ids_deleted.append(seed_id)
        except CensysSeedNotFoundException:  # pragma: no cover
            with lock:
                nonlocal seed_ids_not_found
                seed_ids_not_found.append(seed_id)
        progress.update(task_id, advance=1)

    # Create a rich Progress instance
    with Progress() as progress:
        progress_task_id = progress.add_task(
            "[cyan]Deleting[/cyan]", total=len(seeds_to_delete)
        )
        tasks = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
            # Submit requests using the executor
            for seed_id in seed_ids_to_delete:
                if isinstance(seed_id, str):  # pragma: no cover
                    console.print(f"Invalid seed id {seed_id}")
                    continue
                task = executor.submit(delete_seed, seed_id, progress, progress_task_id)
                tasks.append(task)

            # Wait for all requests to complete
            concurrent.futures.wait(tasks)

    console.print(f"Deleted {len(seed_ids_deleted)} seeds.")
    if len(seed_ids_not_found) > 0:
        console.print(
            f"Unable to delete {len(seed_ids_not_found)} seeds because they were not present."
        )


def cli_delete_all_seeds(args: argparse.Namespace):
    """Delete all seeds subcommand.

    Args:
        args (Namespace): Argparse Namespace.
    """
    if not args.force:
        delete_all = Confirm.ask(
            "Are you sure you want to delete all seeds?",
            default=False,
            show_default=True,
            console=console,
        )
        console_clear_line()
        if not delete_all:
            sys.exit(1)

    s = Seeds(args.api_key)

    console.print("Getting seeds...")
    seeds = s.get_seeds()
    console_clear_line()

    # Create a lock to protect shared variables
    lock = threading.Lock()
    seeds_delete_count = 0

    def delete_seed(seed_id: int, progress: Progress, task_id: TaskID):
        s.delete_seed_by_id(seed_id)
        with lock:
            nonlocal seeds_delete_count
            seeds_delete_count += 1
        progress.update(task_id, advance=1)

    # Create a rich Progress instance
    with Progress() as progress:
        progress_task_id = progress.add_task("[cyan]Deleting[/cyan]", total=len(seeds))
        tasks = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
            # Submit requests using the executor
            for seed in seeds:
                task = executor.submit(
                    delete_seed, seed["id"], progress, progress_task_id
                )
                tasks.append(task)

            # Wait for all requests to complete
            concurrent.futures.wait(tasks)

    console.print(f"Deleted {seeds_delete_count} of {len(seeds)} total seeds.")


def cli_delete_seeds_with_label(args: argparse.Namespace):
    """Delete seeds with label subcommand.

    Args:
        args (Namespace): Argparse Namespace.
    """
    s = Seeds(args.api_key)
    s.delete_seeds_by_label(args.label)
    console.print(f'Deleted seeds with label "{args.label}".')


def cli_replace_seeds_with_label(args: argparse.Namespace):
    """Replace seeds with label subcommand.

    Args:
        args (Namespace): Argparse Namespace.
    """
    seeds_to_add = get_seeds_from_params(args, "replace-labeled-seeds")
    s = Seeds(args.api_key)

    res = s.replace_seeds_by_label(args.label, seeds_to_add, True)
    console.print(
        f"Removed {len(res['removedSeeds'])} seeds.  Added {len(res['addedSeeds'])} seeds.  Skipped {len(res['skippedReservedSeeds'])} reserved seeds."
    )

    if args.verbose:  # pragma: no cover
        added_seeds = res.get("addedSeeds", [])
        if len(added_seeds) > 0:
            console.print("The following seed(s) were added.")
            for added_seed in added_seeds:
                console.print(f"    {added_seed}")
        removed_seeds = res.get("removedSeeds", [])
        if len(removed_seeds) > 0:
            console.print("The following seed(s) were removed.")
            for removed_seed in removed_seeds:
                console.print(f"    {removed_seed}")
        skipped_seeds = res.get("skippedReservedSeeds", [])
        if len(skipped_seeds) > 0:
            console.print(
                "The following seed(s) were not added because they are reserved."
            )
            for skipped_seed in skipped_seeds:
                console.print(f"    {skipped_seed}")


def cli_list_seeds(args: argparse.Namespace):
    """List seeds subcommand.

    Args:
        args (Namespace): Argparse Namespace.
    """
    s = Seeds(args.api_key)
    res = s.get_seeds(args.type, args.label)
    if args.csv:
        console.print("id,type,value,label,source,createdOn")
        for seed in res:
            console.print(
                f"{seed['id']},{seed['type']},{seed['value']},{seed['label']},{seed['source']},{seed['createdOn']}"  # noqa: E231
            )
    else:
        console.print_json(json.dumps(res))


def add_seed_arguments(parser: argparse._SubParsersAction, is_delete=False) -> None:
    """Add seed arguments to parser.

    Args:
        parser (argparse._SubParsersAction): Parser.
        is_delete (Boolean): Is this a delete command.
    """
    if not is_delete:
        parser.add_argument(  # type: ignore[attr-defined]
            "--default-type",
            help="type of the seed(s) if type is not already provided (default: %(default)s)",
            choices=SEED_TYPES,
            default="IP_ADDRESS",
        )
    parser.add_argument("--csv", help="process input in CSV format", action="store_true")  # type: ignore[attr-defined]
    seeds_group = parser.add_mutually_exclusive_group(required=True)  # type: ignore[attr-defined]
    seeds_group.add_argument(
        "--input-file",
        "-i",
        help="input file name containing valid seeds in JSON format, unless --csv is specified (use - for stdin)",
        type=str,
    )
    seeds_group.add_argument(
        "--json", "-j", help="input string containing valid json seeds", type=str
    )
    seeds_group.add_argument(
        "--nmap-xml", help="input file name containing valid xml nmap output", type=str
    )


def include(parent_parser: argparse._SubParsersAction, parents: dict):
    """Include this subcommand into the parent parser.

    Args:
        parent_parser (argparse._SubParsersAction): Parent parser.
        parents (dict): Parent arg parsers.
    """
    asm_parser = parent_parser.add_parser(
        "asm", description="Interact with the Censys ASM API", help="interact with ASM"
    )

    def add_verbose(parser):
        parser.add_argument(
            "-v",
            "--verbose",
            help="verbose output",
            action="store_true",
        )

    asm_subparser = asm_parser.add_subparsers()

    # Add config command
    config_parser = asm_subparser.add_parser(
        "config",
        description="Configure Censys ASM API Settings",
        help="configure Censys ASM API settings",
    )
    config_parser.set_defaults(func=cli_asm_config)

    add_parser = asm_subparser.add_parser(
        "add-seeds",
        description="Add seeds to ASM",
        help="add seeds",
        parents=[parents["asm_auth"]],
    )
    add_verbose(add_parser)
    add_seed_arguments(add_parser)
    add_parser.add_argument(
        "-l",
        "--label",
        help='label to apply to seeds without label (default: "")',
        type=str,
        default="",
    )
    add_parser.set_defaults(func=cli_add_seeds)

    delete_parser = asm_subparser.add_parser(
        "delete-seeds",
        description="Delete ASM seeds",
        help="delete seeds",
        parents=[parents["asm_auth"]],
    )
    add_verbose(delete_parser)
    add_seed_arguments(delete_parser, True)
    delete_parser.set_defaults(func=cli_delete_seeds)

    delete_all_parser = asm_subparser.add_parser(
        "delete-all-seeds",
        description="Delete all ASM seeds",
        help="delete all seeds",
        parents=[parents["asm_auth"]],
    )
    delete_all_parser.add_argument(
        "-f",
        "--force",
        help="force delete all (no confirmation prompt)",
        action="store_true",
    )
    add_verbose(delete_all_parser)
    delete_all_parser.set_defaults(func=cli_delete_all_seeds)

    delete_with_label_parser = asm_subparser.add_parser(
        "delete-labeled-seeds",
        description="Delete all ASM seeds with specified label",
        help="delete all seeds having label",
        parents=[parents["asm_auth"]],
    )
    delete_with_label_parser.add_argument(
        "-l",
        "--label",
        help="label for which to delete all seeds",
        type=str,
        default="",
        required=True,
    )
    add_verbose(delete_with_label_parser)
    delete_with_label_parser.set_defaults(func=cli_delete_seeds_with_label)

    replace_with_label_parser = asm_subparser.add_parser(
        "replace-labeled-seeds",
        description="Replace all ASM seeds with specified label with new seeds",
        help="replace all seeds having label",
        parents=[parents["asm_auth"]],
    )
    replace_with_label_parser.add_argument(
        "-l",
        "--label",
        help="label for which to replace all seeds",
        type=str,
        default="",
        required=True,
    )
    add_verbose(replace_with_label_parser)
    add_seed_arguments(replace_with_label_parser)
    replace_with_label_parser.set_defaults(func=cli_replace_seeds_with_label)

    list_parser = asm_subparser.add_parser(
        "list-seeds",
        description="List all ASM seeds, optionally filtered by label and type",
        help="list seeds",
        parents=[parents["asm_auth"]],
    )
    list_parser.add_argument(
        "-t",
        "--type",
        help="type of the seed to list, if not specified, all types returned",
        choices=SEED_TYPES,
        default="",
    )
    list_parser.add_argument(
        "-l",
        "--label",
        help="label of seeds to list, if not specified, all labels returned",
        type=str,
        default="",
    )
    list_parser.add_argument(
        "--csv", help="output in CSV format (otherwise JSON)", action="store_true"
    )
    add_verbose(list_parser)
    list_parser.set_defaults(func=cli_list_seeds)
