"""
Base for interacting with the Censys ASM API.
"""
# pylint: disable=too-many-arguments
import os

from math import inf
from typing import Generator, Type, Optional
from requests.models import Response
from censys.exceptions import (
    CensysMissingApiKeyException,
    CensysAsmException,
    CensysExceptionMapper,
)

from censys.base import CensysAPIBase
from censys.config import get_config, DEFAULT


class CensysAsmAPI(CensysAPIBase):
    """
    This is the base class for ASM's Seeds, Assets, and Events classes
    """

    DEFAULT_URL: str = "https://app.censys.io/api/v1"
    """Default ASM API base URL."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        url = kwargs.pop("url", self.DEFAULT_URL)
        CensysAPIBase.__init__(self, url=url, **kwargs)

        # Gets config file
        config = get_config()

        # Try to get credentials
        self._api_key = (
            api_key
            or os.getenv("CENSYS_ASM_API_KEY")
            or config.get(DEFAULT, "asm_api_key")
        )

        if not self._api_key:
            raise CensysMissingApiKeyException("No ASM API key configured.")

        self._session.headers.update(
            {"Content-Type": "application/json", "Censys-Api-Key": self._api_key}
        )

    def _get_exception_class(  # type: ignore
        self, res: Response
    ) -> Type[CensysAsmException]:
        return CensysExceptionMapper.ASM_EXCEPTIONS.get(
            res.json()["errorCode"], CensysAsmException
        )

    def _get_page(
        self, path: str, page_number: int = 1, page_size: Optional[int] = None
    ) -> Generator[dict, None, None]:
        """
        Fetches paginated ASM resource API results.

        Args:
            path (str): The API url endpoint.
            page_number (int, optional): Page number to begin at when getting results.
            page_size (int, optional): Number of results to return per HTTP request

        Returns:
            generator: The resource result set returned.
        """

        total_pages = inf

        while page_number <= total_pages:
            args = {"pageNumber": page_number, "pageSize": page_size or 500}

            res = self._get(path, args=args)
            page_number = int(res["pageNumber"]) + 1
            total_pages = int(res["totalPages"])

            if "comments" in path:
                for comment in res["comments"]:
                    yield comment
            else:
                for asset in res["assets"]:
                    yield asset

    def _get_logbook_page(
        self, path: str, args: Optional[dict] = None
    ) -> Generator[dict, None, None]:
        """
        Fetches paginated ASM logbook API events.

        Args:
            path (str): The API url endpoint.
            args (dict, optional): URL args that are mapped to params (cursor).

        Returns:
            generator: The event result set returned.
        """

        end_of_events = False

        while not end_of_events:
            res = self._get(path, args=args)
            end_of_events = res["endOfEvents"]
            args = {"cursor": res["nextCursor"]}

            for event in res["events"]:
                yield event
