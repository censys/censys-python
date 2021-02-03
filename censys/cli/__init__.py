#!/usr/bin/env python
"""
Interact with the Censys API's through the command line.
"""

import os
import sys
import argparse
from pathlib import Path

from censys.config import get_config, DEFAULT
from censys.cli.search import CensysAPISearch
from censys.cli.hnri import CensysHNRI
from censys.cli.config import cli_config, cli_asm_config


def search(args):
    """
    search subcommand.

    Args:
        args (Namespace): Argparse Namespace.
    """

    censys_args = {}

    if args.start_page:
        censys_args["start_page"] = args.start_page

    if args.max_pages:
        censys_args["max_pages"] = args.max_pages

    if args.api_id:
        censys_args["api_id"] = args.api_id

    if args.api_secret:
        censys_args["api_secret"] = args.api_secret

    censys = CensysAPISearch(**censys_args)

    search_args = {"query": args.query}

    if args.fields:
        search_args["fields"] = args.fields

    if args.overwrite:
        search_args["overwrite"] = args.overwrite

    indexes = {
        "ipv4": censys.search_ipv4,
        "certs": censys.search_certificates,
        "websites": censys.search_websites,
    }

    index_type = args.index_type or args.query_type

    index_func = indexes[index_type]
    results = index_func(**search_args)

    try:
        censys.write_file(results, file_format=args.format, file_path=args.output)
    except ValueError as error:  # pragma: no cover
        print(f"Error writing log file. Error: {error}")


def hnri(args):
    """
    hnri subcommand.

    Args:
        args (Namespace): Argparse Namespace.
    """

    client = CensysHNRI(args.api_id, args.api_secret)

    risks = client.view_current_ip_risks()

    print(risks)


def get_parser() -> argparse.ArgumentParser:
    """
    Gets ArgumentParser for CLI.

    Returns:
        argparse.ArgumentParser
    """

    config = get_config()

    auth = argparse.ArgumentParser(add_help=False)
    auth.add_argument(
        "--api-id",
        default=os.getenv("CENSYS_API_ID") or config.get(DEFAULT, "api_id"),
        required=False,
        help="a Censys API ID \
            (alternatively you can use the env variable CENSYS_API_ID)",
    )
    auth.add_argument(
        "--api-secret",
        default=os.getenv("CENSYS_API_SECRET") or config.get(DEFAULT, "api_secret"),
        required=False,
        help="a Censys API SECRET \
            (alternatively you can use the env variable CENSYS_API_SECRET)",
    )

    parser = argparse.ArgumentParser()
    parser.set_defaults()
    subparsers = parser.add_subparsers()

    # Search Specific Args
    search_parser = subparsers.add_parser(
        "search",
        description="Query Censys Search for resource data by providing a query \
            string, the resource index, and the fields to be returned",
        help="query Censys search",
        parents=[auth],
    )
    search_parser.add_argument(
        "-q",
        "--query",
        type=str,
        required=True,
        help="a string written in Censys Search syntax",
    )

    index_types = ["ipv4", "certs", "websites"]
    index_metavar = "ipv4|certs|websites"
    index_default = "ipv4"
    search_parser.add_argument(
        "--index-type",
        type=str,
        default=index_default,
        choices=index_types,
        metavar=index_metavar,
        help="which resource index to query",
    )
    # Backwards compatibility
    search_parser.add_argument(
        "--query_type",
        type=str,
        default=index_default,
        choices=index_types,
        metavar=index_metavar,
        help=argparse.SUPPRESS,
    )

    search_parser.add_argument(
        "--fields", nargs="+", help="list of index-specific fields"
    )
    search_parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="overwrite instead of append fields returned by default \
            with fields provided in the fields argument",
    )
    search_parser.add_argument(
        "-f",
        "--format",
        type=str,
        default="screen",
        metavar="json|csv|screen",
        help="format of output",
    )
    search_parser.add_argument(
        "-o", "--output", type=Path, help="output file path",
    )
    search_parser.add_argument(
        "--start-page", default=1, type=int, help="page number to start from"
    )
    search_parser.add_argument(
        "--max-pages",
        default=1,
        type=int,
        help="maximum number of pages of results to return",
    )
    search_parser.set_defaults(func=search)

    # HNRI Specific Args
    hnri_parser = subparsers.add_parser(
        "hnri",
        description="Home Network Risk Identifier (H.N.R.I.)",
        help="home network risk identifier",
        parents=[auth],
    )
    hnri_parser.set_defaults(func=hnri)

    # Config Specific Args
    config_parser = subparsers.add_parser(
        "config",
        description="Configure Censys Search API Settings",
        help="configure Censys search API settings",
    )
    config_parser.set_defaults(func=cli_config)

    # ASM Config Args
    asm_config_parser = subparsers.add_parser(
        "config-asm",
        description="Configure Censys ASM API Settings",
        help="configure Censys ASM API settings",
    )
    asm_config_parser.set_defaults(func=cli_asm_config)

    return parser


def main():
    """main cli function"""

    parser = get_parser()

    # Executes by subcommand
    args = parser.parse_args()

    try:
        args.func(args)
    except AttributeError:
        parser.print_help()
        parser.exit()
    except KeyboardInterrupt:  # pragma: no cover
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
