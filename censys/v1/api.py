"""Base for interacting with the Censys Search API."""
import os
from typing import Iterator, List, Optional, Type

from requests.models import Response

from ..base import CensysAPIBase
from ..config import DEFAULT, get_config
from ..exceptions import CensysException, CensysExceptionMapper, CensysSearchException

Fields = Optional[List[str]]


class CensysSearchAPIv1(CensysAPIBase):
    """This class is the base class for all v1 API indexes.

    See CensysAPIBase for additional arguments.

    Args:
        api_id (str): Optional; The API ID provided by Censys.
        api_secret (str): Optional; The API secret provided by Censys.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Raises:
        CensysException: Base Exception Class for the Censys API.
    """

    DEFAULT_URL: str = "https://censys.io/api/v1"
    """Default Search API base URL."""
    INDEX_NAME: Optional[str] = None
    """Name of Censys Index."""

    def __init__(self, *args, **kwargs):
        """Inits CensysSearchAPIv1."""
        # Backwards compatability
        if len(args) == 2:
            kwargs["api_id"] = args[0]
            kwargs["api_secret"] = args[1]

        CensysAPIBase.__init__(self, kwargs.get("url", self.DEFAULT_URL), **kwargs)

        # Gets config file
        config = get_config()

        # Try to get credentials
        self._api_id = (
            kwargs.get("api_id")
            or os.getenv("CENSYS_API_ID")
            or config.get(DEFAULT, "api_id")
        )
        self._api_secret = (
            kwargs.get("api_secret")
            or os.getenv("CENSYS_API_SECRET")
            or config.get(DEFAULT, "api_secret")
        )
        if not self._api_id or not self._api_secret:
            raise CensysException("No API ID or API secret configured.")

        self._session.auth = (self._api_id, self._api_secret)

        # Generate concrete paths to be called
        self.search_path = f"search/{self.INDEX_NAME}"
        self.view_path = f"view/{self.INDEX_NAME}"
        self.report_path = f"report/{self.INDEX_NAME}"

        # Confirm setup
        # self.account()

    def _get_exception_class(  # type: ignore
        self, res: Response
    ) -> Type[CensysSearchException]:
        return CensysExceptionMapper.SEARCH_EXCEPTIONS.get(
            res.status_code, CensysSearchException
        )

    def account(self) -> dict:
        """Gets the current account information.

        This includes email and quota.

        Returns:
            dict: Account response.
        """
        return self._get("account")

    def quota(self) -> dict:
        """Gets the current account's query quota.

        Returns:
            dict: Quota response.
        """
        return self.account()["quota"]

    def metadata(self, query: str) -> dict:
        """Returns metadata of a given search query.

        Args:
            query (str): The query to be executed.

        Returns:
            dict: The metadata of the result set returned.
        """
        data = {"query": query, "page": 1, "fields": []}
        return self._post(self.search_path, data=data).get("metadata", {})

    def paged_search(
        self,
        query: str,
        fields: Fields = None,
        page: int = 1,
        flatten: bool = True,
    ) -> dict:
        """Searches the given index for all records that match the given query.

        Args:
            query (str): The query to be executed.
            fields (Fields): Optional; Fields to be returned in the result set.
            page (int): Optional; The page of the result set. Defaults to 1.
            flatten (bool): Optional; Flattens fields to dot notation. Defaults to True.

        Raises:
            CensysException: Base Exception Class for the Censys API.

        Returns:
            dict: The result set returned.
        """
        try:
            page = int(page)
        except ValueError as error:
            raise CensysException(f"Invalid page value: {page}") from error
        data = {
            "query": query,
            "page": page,
            "fields": fields or [],
            "flatten": flatten,
        }
        return self._post(self.search_path, data=data)

    # pylint: disable=too-many-arguments
    def search(
        self,
        query: str,
        fields: Fields = None,
        page: int = 1,
        max_records: Optional[int] = None,
        flatten: bool = True,
    ) -> Iterator[dict]:
        """Searches the given index for all records that match the given query.

        For more details, see our documentation: https://censys.io/api/v1/docs/search

        Args:
            query (str): The query to be executed.
            fields (Fields): Optional; Fields to be returned in the result set.
            page (int): Optional; The page of the result set. Defaults to 1.
            max_records (int): Optional; The maximum number of records.
            flatten (bool): Optional; Flattens fields to dot notation. Defaults to True.

        Raises:
            CensysException: Base Exception Class for the Censys API.

        Yields:
            dict: The result set returned.
        """
        if fields is None:
            fields = []
        try:
            page = int(page)
        except ValueError as error:
            raise CensysException(f"Invalid page value: {page}") from error
        pages = float("inf")
        data = {"query": query, "page": page, "fields": fields, "flatten": flatten}

        count = 0
        while page <= pages:
            payload = self._post(self.search_path, data=data)
            pages = payload["metadata"]["pages"]
            page += 1
            data["page"] = page

            for result in payload["results"]:
                yield result
                count += 1
                if max_records and count >= max_records:
                    return

    def view(self, document_id: str) -> dict:
        """View the current structured data we have on a specific document.

        For more details, see our documentation: https://censys.io/api/v1/docs/view

        Args:
            document_id (str): The ID of the document you are requesting.

        Returns:
            dict: The result set returned.
        """
        return self._get("/".join((self.view_path, document_id)))

    def report(self, query: str, field: str, buckets: int = 50) -> dict:
        """Creates a report on the breakdown of the values of a field in a result set.

        For more details, see our documentation: https://censys.io/api/v1/docs/report

        Args:
            query (str): The query to be executed.
            field (str): The field you are running a breakdown on.
            buckets (int): Optional; The maximum number of values. Defaults to 50.

        Returns:
            dict: The result set returned.
        """
        data = {"query": query, "field": field, "buckets": int(buckets)}
        return self._post(self.report_path, data=data)


CensysSearchAPI = CensysSearchAPIv1
