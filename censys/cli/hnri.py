from typing import List, Tuple

import requests

from censys.ipv4 import CensysIPv4
from censys.exceptions import (
    CensysCLIException,
    CensysNotFoundException,
)


class CensysHNRI:
    """
    This class searches the Censys API, check the user's current IP for risks.

    Args:
        api_id (str, optional): The API ID provided by Censys.
        api_secret (str, optional): The API secret provided by Censys.
    """

    HIGH_RISK_DEFINITION: List[str] = ["telnet", "redis", "postgres", "vnc"]
    MEDIUM_RISK_DEFINITION: List[str] = ["ssh", "http", "https"]

    def __init__(self, api_id: str, api_secret: str):
        self.index = CensysIPv4(api_id, api_secret)

    @staticmethod
    def get_current_ip() -> str:
        """
        Uses ipify.org to get the current IP address.

        Returns:
            str: IP address.
        """

        response = requests.get("https://api.ipify.org?format=json")
        current_ip = response.json().get("ip")
        return current_ip

    def translate_risk(self, protocols: list) -> Tuple[list, list]:
        """
        Interpret protocols to risks.

        Args:
            protocols (list): List of slash divided ports/protocols.

        Returns:
            Tuple[list, list]: Lists of high and medium risks.
        """

        high_risk = []
        medium_risk = []

        for protocol in protocols:
            port, protocol = protocol.split("/")
            string = f"{protocol} on {port}"
            if protocol in self.HIGH_RISK_DEFINITION:
                high_risk.append({"port": port, "protocol": protocol, "string": string})
            elif protocol in self.MEDIUM_RISK_DEFINITION:
                medium_risk.append(
                    {"port": port, "protocol": protocol, "string": string}
                )
            elif protocol == "banner":
                medium_risk.append(
                    {"port": port, "protocol": "unknown protocol", "string": string}
                )
            else:
                medium_risk.append(
                    {"port": port, "protocol": protocol, "string": string}
                )

        return high_risk, medium_risk

    @staticmethod
    def risks_to_string(high_risk: list, medium_risk: list) -> str:
        """
        Risks to printable string.

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
                + "High Risks Found: \n"
                + "\n".join([risk.get("string") for risk in high_risk])
            )
        else:
            response = response + "You don't have any High Risks in your network\n"
        if len_medium_risk > 0:
            response = (
                response
                + "Medium Risks Found: \n"
                + "\n".join([risk.get("string") for risk in medium_risk])
            )
        else:
            response = response + "You don't have any Medium Risks in your network\n"
        return response

    def view_current_ip_risks(self) -> str:
        """
        Gets protocol information for the current IP and returns any risks.

        Returns:
            str: Printable
        """

        current_ip = self.get_current_ip()

        try:
            results = self.index.view(current_ip)
            protocols = results.get("protocols", [])
            high_risk, medium_risk = self.translate_risk(protocols)
            return self.risks_to_string(high_risk, medium_risk)
        except (CensysNotFoundException, CensysCLIException):
            return "No Risks were found on your network"
