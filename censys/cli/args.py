"""Interact with argparser."""
import os
import argparse
from pathlib import Path

from censys.common.config import get_config, DEFAULT
from .commands import cli_config, cli_asm_config, cli_hnri, cli_search
from .commands.search import INDEXES, V1_INDEXES, V2_INDEXES


def get_parser() -> argparse.ArgumentParser:
    """Gets ArgumentParser for CLI.

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
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        default=False,
        help="display version",
    )
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
        "query",
        type=str,
        help="a string written in Censys Search syntax",
    )

    index_metavar = "|".join(INDEXES)
    index_default = "ipv4"
    search_parser.add_argument(
        "--index-type",
        type=str,
        default=index_default,
        choices=INDEXES,
        metavar=index_metavar,
        help="which resource index to query",
    )
    # Backwards compatibility
    search_parser.add_argument(
        "--query_type",
        type=str,
        default=index_default,
        choices=INDEXES,
        metavar=index_metavar,
        help=argparse.SUPPRESS,
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
        "-o",
        "--output",
        type=Path,
        help="output file path",
    )

    v1_group = search_parser.add_argument_group(
        f"v1 specific arguments ({', '.join(V1_INDEXES)})"
    )
    v1_group.add_argument("--fields", nargs="+", help="list of index-specific fields")
    v1_group.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="overwrite instead of append fields returned by default \
            with fields provided in the fields argument",
    )
    v1_group.add_argument(
        "--max_records",
        type=int,
        help="maximum number of results to return",
    )

    v2_group = search_parser.add_argument_group(
        f"v2 specific arguments ({', '.join(V2_INDEXES)})"
    )
    v2_group.add_argument(
        "--pages",
        default=1,
        type=int,
        help="number of pages of results to return",
    )

    search_parser.set_defaults(func=cli_search)

    # HNRI Specific Args
    hnri_parser = subparsers.add_parser(
        "hnri",
        description="Home Network Risk Identifier (H.N.R.I.)",
        help="home network risk identifier",
        parents=[auth],
    )
    hnri_parser.set_defaults(func=cli_hnri)

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
