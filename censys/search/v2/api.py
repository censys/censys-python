"""Base for interacting with the Censys Search API."""
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Iterable, Iterator, List, Optional, Type

from requests.models import Response

from censys.common.base import CensysAPIBase
from censys.common.config import DEFAULT, get_config
from censys.common.exceptions import (
    CensysException,
    CensysExceptionMapper,
    CensysSearchException,
)
from censys.common.types import Datetime
from censys.common.utils import format_rfc3339
from censys.search.v1.api import CensysSearchAPIv1

Fields = Optional[List[str]]

INDEX_TO_KEY = {"hosts": "ip"}


class CensysSearchAPIv2(CensysAPIBase):
    """This class is the base class for the Hosts index.

    Examples:
        >>> c = CensysSearchAPIv2()
    """

    DEFAULT_URL: str = "https://search.censys.io/api/v2"
    """Default Search API base URL."""
    INDEX_NAME: str = ""
    """Name of Censys Index."""
    v1: CensysSearchAPIv1
    """Search V1 Endpoints on V2"""

    def __init__(
        self, api_id: Optional[str] = None, api_secret: Optional[str] = None, **kwargs
    ):
        """Inits CensysSearchAPIv2.

        See CensysAPIBase for additional arguments.

        Args:
            api_id (str): Optional; The API ID provided by Censys.
            api_secret (str): Optional; The API secret provided by Censys.
            **kwargs: Arbitrary keyword arguments.

        Raises:
            CensysException: Base Exception Class for the Censys API.
        """
        CensysAPIBase.__init__(self, kwargs.pop("url", self.DEFAULT_URL), **kwargs)

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
        self.view_path = f"/{self.INDEX_NAME}/"
        self.search_path = f"/{self.INDEX_NAME}/search"
        self.aggregate_path = f"/{self.INDEX_NAME}/aggregate"
        self.metadata_path = f"/metadata/{self.INDEX_NAME}"
        self.tags_path = "/tags"

        # Set up the v1 API
        v1_kwargs = kwargs.copy()
        v1_kwargs.update(
            {
                "url": "https://search.censys.io/api/v1",
                "api_id": self._api_id,
                "api_secret": self._api_secret,
            }
        )
        self.v1 = CensysSearchAPIv1(**v1_kwargs)

    def _get_exception_class(  # type: ignore
        self, res: Response
    ) -> Type[CensysSearchException]:
        return CensysExceptionMapper.SEARCH_EXCEPTIONS.get(
            res.status_code, CensysSearchException
        )

    def account(self) -> dict:
        """Gets the current account's query quota.

        Returns:
            dict: Quota response.
        """
        # Make account call to v1 endpoint
        return self.v1.account()

    def quota(self) -> dict:
        """Returns metadata of a given search query.

        Returns:
            dict: The metadata of the result set returned.
        """
        return self.account()["quota"]

    class Query(Iterable):
        """Query class that is callable and iterable.

        Object Searches the given index for all records that match the given query.
        For more details, see our documentation: https://search.censys.io/api
        """

        def __init__(
            self,
            api: "CensysSearchAPIv2",
            query: str,
            per_page: Optional[int] = None,
            cursor: Optional[str] = None,
            pages: int = 1,
        ):
            """Inits Query.

            Args:
                api (CensysSearchAPIv2): Parent API object.
                query (str): The query to be executed.
                per_page (int): Optional; The number of results to be returned for each page. Defaults to 100.
                cursor (int): Optional; The cursor of the desired result set.
                pages (int): Optional; The number of pages returned. Defaults to 1.
            """
            self.api = api
            self.query = query
            self.per_page = per_page
            self.cursor = cursor
            self.nextCursor: Optional[str] = None
            self.page = 1
            if pages == -1:
                self.pages = float("inf")
            else:
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

        def view_all(self) -> Dict[str, dict]:
            """View each document returned from query.

            Please note that each result returned by the query will be looked up using the view method.

            Returns:
                Dict[str, dict]: Dictionary mapping documents to that document's result set.
            """
            threads = []
            results = {}

            document_key = INDEX_TO_KEY.get(self.api.INDEX_NAME, "ip")

            with ThreadPoolExecutor(max_workers=20) as executor:
                for hit in self.__call__():
                    document_id = hit[document_key]
                    threads.append(executor.submit(self.api.view, document_id))

                for task in as_completed(threads):
                    result = task.result()
                    results[result[document_key]] = result

            return results

    def search(
        self,
        query: str,
        per_page: Optional[int] = None,
        cursor: Optional[str] = None,
        pages: int = 1,
    ) -> Query:
        """Search current index.

        Searches the given index for all records that match the given query.
        For more details, see our documentation: https://search.censys.io/api

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
        at_time: Optional[Datetime] = None,
    ) -> dict:
        """View document from current index.

        View the current structured data we have on a specific document.
        For more details, see our documentation: https://search.censys.io/api

        Args:
            document_id (str): The ID of the document you are requesting.
            at_time ([str, datetime.date, datetime.datetime]):
                Optional; Fetches a document at a given point in time.

        Returns:
            dict: The result set returned.
        """
        args = {}
        if at_time:
            args["at_time"] = format_rfc3339(at_time)

        return self._get(self.view_path + document_id, args)["result"]

    def aggregate(
        self, query: str, field: str, num_buckets: Optional[int] = None
    ) -> dict:
        """Aggregate current index.

        Creates a report on the breakdown of the values of a field in a result set.
        For more details, see our documentation: https://search.censys.io/api

        Args:
            query (str): The query to be executed.
            field (str): The field you are running a breakdown on.
            num_buckets (int): Optional; The maximum number of values. Defaults to 50.

        Returns:
            dict: The result set returned.
        """
        args = {"q": query, "field": field, "num_buckets": num_buckets}
        return self._get(self.aggregate_path, args)["result"]

    def metadata(self) -> dict:
        """Get current index metadata.

        Returns:
            dict: The result set returned.
        """
        return self._get(self.metadata_path)["result"]

    # Comments

    def get_comments(self, document_id: str) -> List[dict]:
        """Get comments for a document.

        Args:
            document_id (str): The ID of the document you are requesting.

        Returns:
            List[dict]: The list of comments.
        """
        return self._get(self.view_path + document_id + "/comments")["result"][
            "comments"
        ]

    def add_comment(self, document_id: str, contents: str) -> dict:
        """Add comment to a document.

        Args:
            document_id (str): The ID of the document you are requesting.
            contents (str): The contents of the comment.

        Returns:
            dict: The result set returned.
        """
        return self._post(
            self.view_path + document_id + "/comments", data={"contents": contents}
        )["result"]

    # Tags

    def list_all_tags(self) -> List[dict]:
        """List all tags.

        Returns:
            List[dict]: The list of tags.
        """
        return self._get(self.tags_path)["result"]["tags"]

    def create_tag(self, name: str, color: Optional[str] = None) -> dict:
        """Create a tag.

        Args:
            name (str): The name of the tag.
            color (str): Optional; The color of the tag.

        Returns:
            dict: The result set returned.
        """
        tag_def: Dict[str, Any] = {"name": name}
        if color:
            tag_def["metadata"] = {"color": color}
        return self._post(self.tags_path, data=tag_def)["result"]

    def get_tag(self, tag_id: str) -> dict:
        """Get a tag.

        Args:
            tag_id (str): The ID of the tag.

        Returns:
            dict: The result set returned.
        """
        return self._get(self.tags_path + "/" + tag_id)["result"]

    def update_tag(self, tag_id: str, name: str, color: Optional[str] = None) -> dict:
        """Update a tag.

        Args:
            tag_id (str): The ID of the tag.
            name (str): The name of the tag.
            color (str): The color of the tag.

        Returns:
            dict: The result set returned.
        """
        tag_def: Dict[str, Any] = {"name": name}
        if color:
            tag_def["metadata"] = {"color": color}
        return self._put(
            self.tags_path + "/" + tag_id,
            data=tag_def,
        )["result"]

    def delete_tag(self, tag_id: str):
        """Delete a tag.

        Args:
            tag_id (str): The ID of the tag.
        """
        self._delete(self.tags_path + "/" + tag_id)

    def _list_documents_with_tag(
        self, tag_id: str, endpoint: str, keyword: str
    ) -> List[dict]:
        """List documents by tag.

        Args:
            tag_id (str): The ID of the tag.
            endpoint (str): The endpoint to be called.
            keyword (str): The keyword to be used in the endpoint.

        Returns:
            List[dict]: The list of documents.
        """
        return self._get(self.tags_path + "/" + tag_id + "/" + endpoint)["result"][
            keyword
        ]

    def list_tags_on_document(self, document_id: str) -> List[dict]:
        """List tags on a document.

        Args:
            document_id (str): The ID of the document.

        Returns:
            List[dict]: The list of tags.
        """
        return self._get(self.view_path + document_id + "/tags")["result"]["tags"]

    def add_tag_to_document(self, document_id: str, tag_id: str):
        """Add a tag to a document.

        Args:
            document_id (str): The ID of the document.
            tag_id (str): The ID of the tag.
        """
        self._put(self.view_path + document_id + "/tags/" + tag_id)

    def remove_tag_from_document(self, document_id: str, tag_id: str):
        """Remove a tag from a document.

        Args:
            document_id (str): The ID of the document.
            tag_id (str): The ID of the tag.
        """
        self._delete(self.view_path + document_id + "/tags/" + tag_id)
