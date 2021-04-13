"""Base for interacting with the Censys Search API."""
import os
import datetime
from typing import Generator, List, Optional, Type, overload, Union

from requests.models import Response

from ..base import CensysAPIBase
from ..config import DEFAULT, get_config
from ..exceptions import (
    CensysException,
    CensysSearchException,
    CensysExceptionMapper,
)

Fields = Optional[List[str]]


class CensysSearchAPIv2(CensysAPIBase):
    """This class is the base class for the Hosts index.

    See CensysAPIBase for additional arguments.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Raises:
        CensysException: Base Exception Class for the Censys API.

    Examples:
        >>> c = CensysSearchAPIv2()
    """

    DEFAULT_URL: str = "https://search.censys.io/api/v2"
    """Default Search API base URL."""
    INDEX_NAME: str = ""
    """Name of Censys Index."""

    @overload
    def __init__(self, api_id: str, api_secret: str, **kwargs):  # noqa
        ...

    @overload
    def __init__(  # noqa
        self, api_id: str = "YOUR_API_ID", api_secret: str = "YOUR_API_SECRET", **kwargs
    ):
        ...

    def __init__(
        self, api_id: Optional[str] = None, api_secret: Optional[str] = None, **kwargs
    ):
        """Inits CensysSearchAPIv2."""
        CensysAPIBase.__init__(self, kwargs.get("url", self.DEFAULT_URL), **kwargs)

        # Gets config file
        config = get_config()

        # Try to get credentials
        self._api_id = (
            api_id or os.getenv("CENSYS_API_ID") or config.get(DEFAULT, "api_id")
        )
        self._api_secret = (
            api_secret
            or os.getenv("CENSYS_API_SECRET")
            or config.get(DEFAULT, "api_secret")
        )
        if not self._api_id or not self._api_secret:
            raise CensysException("No API ID or API secret configured.")

        self._session.auth = (self._api_id, self._api_secret)

        # Generate concrete paths to be called
        self.search_path = f"{self.INDEX_NAME}/search"
        self.aggregate_path = f"{self.INDEX_NAME}/aggregate"

    def _get_exception_class(  # type: ignore
        self, res: Response
    ) -> Type[CensysSearchException]:
        return CensysExceptionMapper.SEARCH_EXCEPTIONS.get(
            res.status_code, CensysSearchException
        )

    # def account(self) -> dict:
    #     """
    #     Gets the current account information. Including email and quota.

    #     Returns:
    #         dict: Account response.
    #     """

    #     return self._get("account")

    # def quota(self) -> dict:
    #     """
    #     Gets the current account's query quota.

    #     Returns:
    #         dict: Quota response.
    #     """

    #     return self.account()["quota"]

    def search(
        self,
        query: str,
        per_page: Optional[int] = None,
        cursor: Optional[str] = None,
        pages: int = 1,
    ) -> Generator[dict, None, None]:
        """Search current index.

        Searches the given index for all records that match the given query.
        For more details, see our documentation: https://search.censys.io/api/v2/docs

        Args:
            query (str): The query to be executed.
            per_page (Fields): Optional;
                Fields to be returned in the result set. Defaults to 50.
            cursor (int): Optional; The cursor of the desired result set.
            pages (int): Optional; The number of pages returned. Defaults to 1.

        Yields:
            dict: The result set returned.
        """
        args = {"q": query, "per_page": per_page}

        page = 1
        while page <= pages:
            if cursor:
                args["cursor"] = cursor

            payload = self._get(self.search_path, args)
            page += 1
            result = payload["result"]
            cursor = result["links"]["next"]

            yield from result["hits"]

    def view(
        self, document_id: str, at_time: Optional[Union[str, datetime.date]] = None
    ) -> dict:
        """View document from current index.

        View the current structured data we have on a specific document.
        For more details, see our documentation: https://search.censys.io/api/v2/docs

        Args:
            document_id (str): The ID of the document you are requesting.
            at_time ([str, date]):
                Optional; Fetches a document at a given point in time.

        Returns:
            dict: The result set returned.
        """
        args = {}
        if at_time:
            if isinstance(at_time, datetime.date):
                at_time = at_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            args["at_time"] = at_time

        return self._get("/".join((self.INDEX_NAME, document_id)), args)["result"]

    def aggregate(
        self, query: str, field: str, num_buckets: Optional[int] = None
    ) -> dict:
        """Aggregate current index.

        Creates a report on the breakdown of the values of a field in a result set.
        For more details, see our documentation: https://search.censys.io/api/v2/docs

        Args:
            query (str): The query to be executed.
            field (str): The field you are running a breakdown on.
            num_buckets (int): Optional; The maximum number of values. Defaults to 50.

        Returns:
            dict: The result set returned.
        """
        args = {"q": query, "field": field, "num_buckets": num_buckets}
        return self._get(self.aggregate_path, args)["result"]
