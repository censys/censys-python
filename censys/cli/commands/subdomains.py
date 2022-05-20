"""Censys subdomains CLI."""
import argparse
import json
import sys
from typing import List, Set

from censys.cli.utils import console, err_console
from censys.common.exceptions import (
    CensysException,
    CensysRateLimitExceededException,
    CensysUnauthorizedException,
)
from censys.search import CensysCertificates


def print_subdomains(subdomains: Set[str], as_json: bool = False):
    """Print subdomains.

    Args:
        subdomains (Set[str]): Subdomains.
        as_json (bool): Output in JSON format.
    """
    if as_json:
        console.print_json(json.dumps(list(subdomains)))
    else:
        for subdomain in subdomains:
            console.print(f"  - {subdomain}")


def cli_subdomains(args: argparse.Namespace):  # pragma: no cover
    """Subdomain subcommand.

    Args:
        args: Argparse Namespace.
    """
    subdomains = set()
    try:
        client = CensysCertificates(api_id=args.api_id, api_secret=args.api_secret)
        certificate_query = f"parsed.names: {args.domain}"

        with err_console.status(f"Querying {args.domain} subdomains"):
            certificates_search_results = client.search(
                certificate_query, fields=["parsed.names"], max_records=args.max_records
            )

            # Flatten the result, and remove duplicates
            for search_result in certificates_search_results:
                new_subdomains: List[str] = search_result.get("parsed.names", [])
                subdomains.update(
                    [
                        subdomain
                        for subdomain in new_subdomains
                        if subdomain.endswith(args.domain)
                    ]
                )

        # Don't make console prints if we're in json mode
        if not args.json:
            if len(subdomains) == 0:
                err_console.print(f"No subdomains found for {args.domain}")
                return
            console.print(
                f"Found {len(subdomains)} unique subdomain(s) of {args.domain}"
            )
        print_subdomains(subdomains, args.json)
    except CensysRateLimitExceededException:
        err_console.print("Censys API rate limit exceeded")
        print_subdomains(subdomains, args.json)
    except CensysUnauthorizedException:
        err_console.print("Invalid Censys API ID or secret")
        sys.exit(1)
    except CensysException as e:
        err_console.print(str(e))
        sys.exit(1)


def include(parent_parser: argparse._SubParsersAction, parents: dict):
    """Include this subcommand into the parent parser.

    Args:
        parent_parser (argparse._SubParsersAction): Parent parser.
        parents (dict): Parent arg parsers.
    """
    subdomains_parser = parent_parser.add_parser(
        "subdomains",
        description="enumerate subdomains",
        help="enumerate subdomains",
        parents=[parents["auth"]],
    )
    subdomains_parser.add_argument("domain", help="The domain to scan")
    subdomains_parser.add_argument(
        "--max-records", type=int, default=100, help="Max records to query"
    )
    subdomains_parser.add_argument(
        "-j", "--json", action="store_true", help="Output in JSON format"
    )
    subdomains_parser.set_defaults(func=cli_subdomains)
