"""Base for interacting with the Censys Search API."""
import datetime
import os
from typing import Iterable, Iterator, List, Optional, Type, Union

from requests.models import Response

from ..base import CensysAPIBase
from ..config import DEFAULT, get_config
from ..exceptions import CensysException, CensysExceptionMapper, CensysSearchException

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

    class Query(Iterable):
        """Query class that is callable and iterable.

        Object Searches the given index for all records that match the given query.
        For more details, see our documentation: https://search.censys.io/api/v2/docs

        Args:
            api (CensysSearchAPIv2): Parent API object.
            query (str): The query to be executed.
            per_page (int): Optional; The number of results to be returned for each page. Defaults to 100.
            cursor (int): Optional; The cursor of the desired result set.
            pages (int): Optional; The number of pages returned. Defaults to 1.
        """

        def __init__(
            self,
            api: "CensysSearchAPIv2",
            query: str,
            per_page: Optional[int] = None,
            cursor: Optional[str] = None,
            pages: int = 1,
        ):
            """Inits Query."""
            self.api = api
            self.query = query
            self.per_page = per_page
            self.cursor = cursor
            self.nextCursor: Optional[str] = None
            self.page = 1
            self.pages = pages

        def __call__(self, per_page: Optional[int] = None) -> List[dict]:
            """Search current index.

            Args:
                per_page (int): Optional; The number of results to be returned for each page. Defaults to 100.

            Raises:
                StopIteration: Raised when pages have been already received.

            Returns:
                List[dict]: One page worth of result hits.
            """
            if self.page > self.pages:
                raise StopIteration

            args = {
                "q": self.query,
                "per_page": per_page or self.per_page or 100,
                "cursor": self.nextCursor or self.cursor,
            }
            payload = self.api._get(self.api.search_path, args)
            self.page += 1
            result = payload["result"]
            self.nextCursor = result["links"]["next"]
            if result["total"] == 0 or not self.nextCursor:
                self.pages = 0
            return result["hits"]

        def __next__(self) -> List[dict]:
            """Gets next page of search results.

            Returns:
                List[dict]: One page worth of result hits.
            """
            return self.__call__()

        def __iter__(self) -> Iterator[List[dict]]:
            """Gets Iterator.

            Returns:
                Iterable: Returns self.
            """
            return self

    def search(
        self,
        query: str,
        per_page: Optional[int] = None,
        cursor: Optional[str] = None,
        pages: int = 1,
    ) -> Query:
        """Search current index.

        Searches the given index for all records that match the given query.
        For more details, see our documentation: https://search.censys.io/api/v2/docs

        Args:
            query (str): The query to be executed.
            per_page (int): Optional; The number of results to be returned for each page. Defaults to 100.
            cursor (int): Optional; The cursor of the desired result set.
            pages (int): Optional; The number of pages returned. Defaults to 1.

        Returns:
            Query: Query object that can be a callable or an iterable.
        """
        return self.Query(self, query, per_page, cursor, pages)

    def view(
        self,
        document_id: str,
        at_time: Optional[Union[str, datetime.date, datetime.datetime]] = None,
    ) -> dict:
        """View document from current index.

        View the current structured data we have on a specific document.
        For more details, see our documentation: https://search.censys.io/api/v2/docs

        Args:
            document_id (str): The ID of the document you are requesting.
            at_time ([str, datetime.date, datetime.datetime]):
                Optional; Fetches a document at a given point in time.

        Returns:
            dict: The result set returned.
        """
        args = {}
        if at_time:
            if isinstance(at_time, (datetime.date, datetime.datetime)):
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
