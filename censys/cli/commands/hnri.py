"""Censys HNRI CLI."""
import argparse
import sys
import webbrowser
from typing import List, Optional, Tuple

import requests
from rich import print

from censys.common.exceptions import CensysCLIException, CensysNotFoundException
from censys.search import CensysHosts


class CensysHNRI:
    """Searches the Censys API for the user's current IP to scan for risks."""

    HIGH_RISK_DEFINITION: List[str] = ["TELNET", "REDIS", "POSTGRES", "VNC"]
    MEDIUM_RISK_DEFINITION: List[str] = ["SSH", "HTTP", "HTTPS"]

    def __init__(self, api_id: Optional[str] = None, api_secret: Optional[str] = None):
        """Inits CensysHNRI.

        Args:
            api_id (str): Optional; The API ID provided by Censys.
            api_secret (str): Optional; The API secret provided by Censys.
        """
        self.index = CensysHosts(api_id, api_secret)

    @staticmethod
    def get_current_ip() -> str:
        """Uses ipify.org to get the current IP address.

        Returns:
            str: IP address.
        """
        response = requests.get("https://api.ipify.org?format=json")
        current_ip = str(response.json().get("ip"))
        return current_ip

    def translate_risk(self, services: List[dict]) -> Tuple[List[dict], List[dict]]:
        """Interpret protocols to risks.

        Args:
            services (list): List of services.

        Returns:
            Tuple[list, list]: Lists of high and medium risks.
        """
        high_risk = []
        medium_risk = []

        for service in services:
            port = service.get("port")
            protocol = service.get("service_name")
            string = f"{protocol} on {port}"
            if protocol in self.HIGH_RISK_DEFINITION:
                high_risk.append({"port": port, "protocol": protocol, "string": string})
            elif protocol in self.MEDIUM_RISK_DEFINITION:
                medium_risk.append(
                    {"port": port, "protocol": protocol, "string": string}
                )
            else:
                medium_risk.append(
                    {"port": port, "protocol": protocol, "string": string}
                )

        return high_risk, medium_risk

    @staticmethod
    def risks_to_string(high_risk: list, medium_risk: list) -> str:
        """Risks to printable string.

        Args:
            high_risk (list): Lists of high risks.
            medium_risk (list): Lists of medium risks.

        Raises:
            CensysCLIException: No information/risks found.

        Returns:
            str: Printable string for CLI.
        """
        len_high_risk = len(high_risk)
        len_medium_risk = len(medium_risk)

        if len_high_risk + len_medium_risk == 0:
            raise CensysCLIException

        response = ""
        if len_high_risk > 0:
            response = (
                response
                + "[bold red]:exclamation: High Risks Found:[/bold red] \n"
                + "\n".join([risk.get("string") for risk in high_risk])
            )
        else:
            response = response + "You don't have any High Risks in your network\n"
        if len_medium_risk > 0:
            response = (
                response
                + "[bold orange]:grey_exclamation: Medium Risks Found:[/bold orange] \n"
                + "\n".join([risk.get("string") for risk in medium_risk])
            )
        else:
            response = response + "You don't have any Medium Risks in your network\n"
        return response

    def view_current_ip_risks(self) -> str:
        """Gets protocol information for the current IP and returns any risks.

        Returns:
            str: Printable
        """
        current_ip = self.get_current_ip()

        try:
            results = self.index.view(current_ip)
            services = results.get("services", [])
            high_risk, medium_risk = self.translate_risk(services)
            return self.risks_to_string(high_risk, medium_risk)
        except (CensysNotFoundException, CensysCLIException):
            return (
                "[green]:white_check_mark: No Risks were found on your network[/green]"
            )


def cli_hnri(args: argparse.Namespace):
    """HNRI subcommand.

    Args:
        args (Namespace): Argparse Namespace.
    """
    if args.open:
        webbrowser.open("https://search.censys.io/me")
        sys.exit(0)

    client = CensysHNRI(args.api_id, args.api_secret)

    risks = client.view_current_ip_risks()

    print(risks)


def include(parent_parser: argparse._SubParsersAction, parents: dict):
    """Include this subcommand into the parent parser.

    Args:
        parent_parser (argparse._SubParsersAction): Parent parser.
        parents (dict): Parent arg parsers.
    """
    hnri_parser = parent_parser.add_parser(
        "hnri",
        description="Home Network Risk Identifier (H.N.R.I.)",
        help="home network risk identifier",
        parents=[parents["auth"]],
    )
    hnri_parser.add_argument(
        "--open",
        action="store_true",
        help="open your IP in browser",
    )
    hnri_parser.set_defaults(func=cli_hnri)
