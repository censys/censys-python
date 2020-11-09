"""
Class for interfacing with the Censys Logbook API.
"""
from typing import Optional, Generator, List
from datetime import datetime


class Events:
    """
    Events API class
    """

    def __init__(self, client):
        self.client = client
        self.base_path = "logbook"

    def get_cursor(
        self, start: Optional[datetime] = None, filters: Optional[List[str]] = None
    ) -> str:
        """
        Requests a logbook cursor.

        Args:
            start (datetime, optional): Seed type ['IP_ADDRESS', 'DOMAIN_NAME', 'CIDR', 'ASN'].
            filters (list, optional): List of filters applied to logbook search results.

        Returns:
            str: Cursor result.
        """

        path = f"{self.base_path}-cursor"
        data = format_data(start=start, filters=filters)

        return self.client._post(path, data=data)["cursor"]

    def get_events(self, cursor: Optional[str] = None) -> Generator[dict, None, None]:
        """
        Requests a logbook cursor.

        Args:
            cursor (str, optional): Logbook cursor.

        Returns:
            generator: Logbook events results.
        """

        args = {"cursor": cursor}

        return self.client._get_logbook_page(self.base_path, args)


class Filters:
    """
    Logbook filters class
    """

    CERT = "CERT"
    CERT_RISK = "CERT_RISK"
    DOMAIN = "DOMAIN"
    DOMAIN_EXPIRATION_DATE = "DOMAIN_EXPIRATION_DATE"
    DOMAIN_MAIL_EXCHANGE_SERVER = "DOMAIN_MAIL_EXCHANGE_SERVER"
    DOMAIN_NAME_SERVER = "DOMAIN_NAME_SERVER"
    DOMAIN_REGISTRAR = "DOMAIN_REGISTRAR"
    DOMAIN_RISK = "DOMAIN_RISK"
    DOMAIN_SUBDOMAIN = "DOMAIN_SUBDOMAIN"
    HOST = "HOST"
    HOST_CERT = "HOST_CERT"
    HOST_PORT = "HOST_PORT"
    HOST_PROTOCOL = "HOST_PROTOCOL"
    HOST_RISK = "HOST_RISK"
    HOST_SOFTWARE = "HOST_SOFTWARE"
    HOST_VULNERABILITY = "HOST_VULNERABILITY"


def format_data(
    start: Optional[datetime] = None, filters: Optional[str] = None
) -> dict:
    """
    Formats cursor request data into a start date/id and filter list

    Args:
        start (datetime, optional): Seed type ['IP_ADDRESS', 'DOMAIN_NAME', 'CIDR', 'ASN'].
        filters (list, optional): List of filters applied to logbook search results.

    Returns:
        dict: Formatted logbook cursor request data
    """

    data = {}

    if filters:
        data["filter"] = {"type": filters}
    if type(start) == int:
        data["idFrom"] = start
    elif start:
        data["dateFrom"] = start

    return data
