"""Base for interacting with the Censys ASM API."""
# pylint: disable=too-many-arguments
import os
from math import inf
from typing import Iterator, Optional, Type

from requests.models import Response

from censys.base import CensysAPIBase
from censys.config import DEFAULT, get_config
from censys.exceptions import CensysAsmException, CensysException, CensysExceptionMapper


class CensysAsmAPI(CensysAPIBase):
    """This is the base class for ASM's Seeds, Assets, and Events classes.

    Args:
        api_key (str): Optional; The API Key provided by Censys.
        **kwargs: Arbitrary keyword arguments.

    Raises:
        CensysException: Base Exception Class for the Censys API.
    """

    DEFAULT_URL: str = "https://app.censys.io/api/v1"
    """Default ASM API base URL."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Inits CensysAsmAPI."""
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
            raise CensysException("No ASM API key configured.")

        self._session.headers.update(
            {"Content-Type": "application/json", "Censys-Api-Key": self._api_key}
        )

    def _get_exception_class(  # type: ignore
        self, res: Response
    ) -> Type[CensysAsmException]:
        return CensysExceptionMapper.ASM_EXCEPTIONS.get(
            res.json().get("errorCode"), CensysAsmException
        )

    def _get_page(
        self, path: str, page_number: int = 1, page_size: Optional[int] = None
    ) -> Iterator[dict]:
        """Fetches paginated ASM resource API results.

        Args:
            path (str): The API url endpoint.
            page_number (int): Optional; Page number to begin at when getting results.
            page_size (int):
                Optional; Number of results to return per HTTP request. Defaults to 500.

        Yields:
            dict: The resource result returned.
        """
        total_pages = inf

        while page_number <= total_pages:
            args = {"pageNumber": page_number, "pageSize": page_size or 500}

            res = self._get(path, args=args)
            page_number = int(res["pageNumber"]) + 1
            total_pages = int(res["totalPages"])

            keyword = "assets"
            if "comments" in path:
                keyword = "comments"
            elif "tags" in path:
                keyword = "tags"
            elif "subdomains" in path:
                keyword = "subdomains"

            yield from res[keyword]

    def _get_logbook_page(
        self, path: str, args: Optional[dict] = None
    ) -> Iterator[dict]:
        """Fetches paginated ASM logbook API events.

        Args:
            path (str): The API url endpoint.
            args (dict): Optional; URL args that are mapped to params (cursor).

        Yields:
            dict: The event result returned.
        """
        end_of_events = False

        while not end_of_events:
            res = self._get(path, args=args)
            end_of_events = res["endOfEvents"]
            args = {"cursor": res["nextCursor"]}

            yield from res["events"]
