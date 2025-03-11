"""Censys Platform CLI commands."""

import argparse
import json
import os
import sys
from typing import Any, Dict

from rich.prompt import Confirm, Prompt

from censys.cli.utils import console, write_file
from censys.common.config import DEFAULT, get_config, write_config
from censys.platform import CensysPlatformClient


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


def get_platform_client() -> CensysPlatformClient:
    """Get a Censys Platform client.

    Returns:
        CensysPlatformClient: The platform client.
    """
    config = get_config()
    token = os.environ.get("CENSYS_PLATFORM_TOKEN") or config.get(
        DEFAULT, "platform_token", fallback=None
    )
    org_id = os.environ.get("CENSYS_ORGANIZATION_ID") or config.get(
        DEFAULT, "platform_org_id", fallback=None
    )

    if not token:
        console.print(
            "[red]Error: Censys Platform Token is required.[/red]\n"
            "Set the CENSYS_PLATFORM_TOKEN environment variable "
            "or configure it using 'censys platform config'"
        )
        sys.exit(1)

    if not org_id:
        console.print(
            "[red]Error: Censys Organization ID is required.[/red]\n"
            "Set the CENSYS_ORGANIZATION_ID environment variable "
            "or configure it using 'censys platform config'"
        )
        sys.exit(1)

    return CensysPlatformClient(token=token, organization_id=org_id)


def cli_platform_search(args: argparse.Namespace):  # pragma: no cover
    """Platform search subcommand.

    Args:
        args: Argparse Namespace.
    """
    client = get_platform_client()
    search = client.search

    # Prepare fields parameter
    fields = None
    if args.fields:
        fields = [field.strip() for field in args.fields.split(",")]

    # Prepare sort parameter
    sort = None
    if args.sort:
        sort = [sort_field.strip() for sort_field in args.sort.split(",")]

    # Use the ResultPaginator
    paginator = search.search(
        args.query,
        page_size=args.page_size,
        pages=args.pages,
        fields=fields,
        sort=sort,
    )

    # Structure to hold the results
    all_results: Dict[str, Any] = {"result": {}}

    # If only requesting one page, use get_page for efficiency
    if args.pages == 1:
        # Just get the first page without pagination machinery
        hits = paginator.get_page()
        # Query once to get the total
        paginator.get_page()
        all_results["result"] = {
            "hits": hits,
            "total": paginator.total,
        }
    else:
        # Get all requested pages
        all_hits = paginator.get_all_results()
        all_results["result"] = {
            "hits": all_hits,
            "total": paginator.total,
        }

    # Output results
    if args.output:
        write_file(all_results, args.output)
        console.print(f"[green]Search results written to {args.output}[/green]")
    else:
        console.print(json.dumps(all_results, indent=2))


def cli_platform_view(args: argparse.Namespace):  # pragma: no cover
    """Platform view subcommand.

    Args:
        args: Argparse Namespace.
    """
    client = get_platform_client()

    # Determine the resource type and call the appropriate API
    if args.resource_type == "host":
        result = client.hosts.view(args.resource_id)
    elif args.resource_type == "certificate":
        result = client.certificates.view(args.resource_id)
    elif args.resource_type == "webproperty":
        result = client.webproperties.view(args.resource_id)
    else:
        console.print(f"[red]Unknown resource type: {args.resource_type}[/red]")
        sys.exit(1)

    # Output results
    if args.output:
        write_file(result, args.output)
        console.print(f"[green]View results written to {args.output}[/green]")
    else:
        console.print(json.dumps(result, indent=2))


def cli_platform_aggregate(args: argparse.Namespace):  # pragma: no cover
    """Platform aggregate subcommand.

    Args:
        args: Argparse Namespace.
    """
    client = get_platform_client()
    search = client.search

    # Execute aggregate query
    results = search.aggregate(
        args.query,
        args.field,
        number_of_buckets=args.num_buckets,
    )

    # Output results
    if args.output:
        write_file(results, args.output)
        console.print(f"[green]Aggregate results written to {args.output}[/green]")
    else:
        console.print(json.dumps(results, indent=2))


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

    # Platform search command
    search_parser = platform_subparsers.add_parser(
        "search",
        description="Search the Censys Platform using a query string",
        help="search the Censys Platform",
    )
    search_parser.add_argument(
        "query",
        type=str,
        help="a string written in Censys Search syntax",
    )
    search_parser.add_argument(
        "--page-size",
        type=int,
        default=100,
        help="number of results per page (default: 100)",
    )
    search_parser.add_argument(
        "--pages",
        type=int,
        default=-1,
        help="number of pages to fetch (-1 for all pages)",
    )
    search_parser.add_argument(
        "--fields",
        type=str,
        help="comma-separated list of fields to return",
    )
    search_parser.add_argument(
        "--sort",
        type=str,
        help="comma-separated list of fields to sort on",
    )
    search_parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="json output file path",
    )
    search_parser.set_defaults(func=cli_platform_search)

    # Platform view command
    view_parser = platform_subparsers.add_parser(
        "view",
        description="View details of a specific resource in the Censys Platform",
        help="view resource details",
    )
    view_parser.add_argument(
        "resource_type",
        type=str,
        choices=["host", "certificate", "webproperty"],
        help="type of resource to view",
    )
    view_parser.add_argument(
        "resource_id",
        type=str,
        help="ID of the resource to view (e.g. IP address, certificate hash, domain name)",
    )
    view_parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="json output file path",
    )
    view_parser.set_defaults(func=cli_platform_view)

    # Platform aggregate command
    aggregate_parser = platform_subparsers.add_parser(
        "aggregate",
        description="Aggregate data from the Censys Platform",
        help="aggregate platform data",
    )
    aggregate_parser.add_argument(
        "query",
        type=str,
        help="a string written in Censys Search syntax",
    )
    aggregate_parser.add_argument(
        "field",
        type=str,
        help="field to aggregate on",
    )
    aggregate_parser.add_argument(
        "--num-buckets",
        type=int,
        default=50,
        help="number of buckets to return (default: 50)",
    )
    aggregate_parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="json output file path",
    )
    aggregate_parser.set_defaults(func=cli_platform_aggregate)
