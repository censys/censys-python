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
from censys.search import CensysCerts, CensysHosts


def sort_subdomains(base_domain: str, subdomains: Set[str]) -> List[str]:
    """Sort subdomains.

    Args:
        base_domain (str): Base domain.
        subdomains (Set[str]): Subdomains.

    Returns:
        List[str]: Sorted subdomains.
    """
    # Sort the subdomains based on their domain components, in reverse order.
    sorted_subdomains = sorted(subdomains, key=lambda x: x.split(".")[::-1])

    return sorted_subdomains


def print_subdomains(base_domain: str, subdomains: Set[str], as_json: bool = False):
    """Print subdomains.

    Args:
        base_domain (str): Base domain.
        subdomains (Set[str]): Subdomains.
        as_json (bool): Output in JSON format.
    """
    # Sort the subdomains
    sorted_subdomains = sort_subdomains(base_domain, subdomains)

    # Print the subdomains
    if as_json:
        console.print_json(json.dumps(sorted_subdomains))
    else:
        for subdomain in sorted_subdomains:
            console.print(f"  - {subdomain}")


def cli_subdomains(args: argparse.Namespace):  # pragma: no cover
    """Subdomain subcommand.

    Args:
        args: Argparse Namespace.
    """
    # Get the domain
    base_domain = args.domain

    # Create a set to store the subdomains
    subdomains = set()

    try:
        # Query the Censys Certificates index
        certs_client = CensysCerts(api_id=args.api_id, api_secret=args.api_secret)
        certs_query = f"names: {base_domain}"

        with err_console.status(f"Querying {base_domain} subdomains"):
            query = certs_client.search(
                certs_query, per_page=100, pages=args.pages
            )  # 100 is the max per page

            # Flatten the result, and remove duplicates
            for hits in query:
                for cert in hits:
                    new_subdomains_certs: List[str] = cert.get("names", [])
                    subdomains.update(
                        [
                            subdomain
                            for subdomain in new_subdomains_certs
                            if subdomain.endswith(base_domain)
                        ]
                    )

        # Query the Censys Hosts index
        hosts_client = CensysHosts(api_id=args.api_id, api_secret=args.api_secret)
        hosts_query = f"dns.names: {base_domain} or dns.reverse_dns.names: {base_domain} or name: {base_domain}"

        with err_console.status(f"Querying {base_domain} subdomains"):
            query = hosts_client.search(hosts_query, per_page=100, pages=args.pages)

            # Flatten the result, and remove duplicates
            for hits in query:
                for host in hits:
                    new_subdomains_hosts: List[str] = []
                    name = host.get("name")
                    if name:
                        new_subdomains_hosts.append(name)

                    # Get the subdomains from the DNS object
                    dns_obj = host.get("dns", {})
                    new_subdomains_hosts.extend(dns_obj.get("names", []))
                    new_subdomains_hosts.extend(
                        dns_obj.get("reverse_dns", {}).get("names", [])
                    )

                    # Get the subdomains from the names object
                    subdomains.update(
                        [
                            subdomain
                            for subdomain in new_subdomains_hosts
                            if subdomain.endswith(base_domain)
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
        print_subdomains(base_domain, subdomains, args.json)
    except CensysRateLimitExceededException:
        err_console.print("Censys API rate limit exceeded")
        print_subdomains(base_domain, subdomains, args.json)
    except CensysUnauthorizedException:
        err_console.print("Invalid Censys API ID or secret")
        sys.exit(1)
    except CensysException as e:
        err_console.print(str(e))
        print_subdomains(base_domain, subdomains, args.json)
        sys.exit(1)
    except KeyboardInterrupt:
        err_console.print("Caught Ctrl-C, exiting...")
        print_subdomains(base_domain, subdomains, args.json)
        sys.exit(1)


def include(parent_parser: argparse._SubParsersAction, parents: dict):
    """Include this subcommand into the parent parser.

    Args:
        parent_parser (argparse._SubParsersAction): Parent parser.
        parents (dict): Parent arg parsers.
    """
    subdomains_parser = parent_parser.add_parser(
        "subdomains",
        description="Enumerates subdomains using the Censys Search Certificates and Hosts indices",
        help="enumerate subdomains",
        parents=[parents["auth"]],
    )
    subdomains_parser.add_argument("domain", help="The base domain to search for")
    subdomains_parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Max records to query each index (default: 1)",
    )
    subdomains_parser.add_argument(
        "-j", "--json", action="store_true", help="Output in JSON format"
    )
    subdomains_parser.set_defaults(func=cli_subdomains)
