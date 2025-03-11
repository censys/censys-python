"""Base for interacting with the Censys ASM API."""

import os
from math import inf
from typing import Iterator, Optional, Type

from requests.models import Response

from censys.common.base import CensysAPIBase
from censys.common.config import DEFAULT, get_config
from censys.common.exceptions import (
    CensysAPIException,
    CensysException,
    CensysExceptionMapper,
    CensysInternalServerErrorException,
)


class CensysAsmAPI(CensysAPIBase):
    """This is the base class for ASM's Seeds, Assets, and Events classes."""

    DEFAULT_URL: str = "https://app.censys.io/api"
    """Default ASM API base URL."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Inits CensysAsmAPI.

        Args:
            api_key (str): Optional; The API Key provided by Censys.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            CensysException: Base Exception Class for the Censys API.
        """
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
    ) -> Type[CensysAPIException]:
        try:
            # First try to get error code from JSON response
            json_data = res.json()
            error_code = json_data.get("errorCode")
            if error_code:
                # ASM has its own error codes, use the ASM mapper
                return CensysExceptionMapper._get_exception_class(error_code, "asm")

            # Handle specific HTTP status codes for ASM
            if res.status_code == 500:
                return CensysInternalServerErrorException
        except (ValueError, KeyError):
            # If JSON parsing fails, check status code first
            if res.status_code == 500:
                return CensysInternalServerErrorException
        else:  # pragma: no cover
            # Otherwise use HTTP status code with ASM mapper
            return CensysExceptionMapper._get_exception_class(res.status_code, "asm")

    def _get_page(
        self,
        path: str,
        page_number: int = 1,
        page_size: Optional[int] = None,
        args: Optional[dict] = None,
        keyword: str = "assets",
    ) -> Iterator[dict]:
        """Fetches paginated ASM resource API results.

        Args:
            path (str): The API url endpoint.
            page_number (int): Optional; Page number to begin at when getting results.
            page_size (int):
                Optional; Number of results to return per HTTP request. Defaults to 500.
            args (dict): Optional; URL args that are mapped to params.
            keyword (str): Optional; The keyword to iterate over in the results.

        Yields:
            dict: The resource result returned.
        """
        total_pages = inf
        args = args or {}

        while page_number <= total_pages:
            args.update({"pageNumber": page_number, "pageSize": page_size or 500})

            res = self._get(path, args=args)
            page_number = int(res["pageNumber"]) + 1
            total_pages = int(res["totalPages"])

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

    def get_workspace_id(self) -> str:
        """Get the workspace ID.

        Returns:
            str: The workspace ID.
        """
        return self._get("/integrations/v1/account")["workspaceId"]
