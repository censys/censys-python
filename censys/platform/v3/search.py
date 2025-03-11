"""Interact with the Censys Platform Search API."""

import warnings
from typing import Any, Dict, Iterable, Iterator, List, Optional, Union

from .api import CensysPlatformAPIv3


class ResultPaginator(Iterable):
    """Iterator for search results that handles pagination automatically.

    This class provides a convenient way to iterate through all pages of search results
    without manually handling cursors and pagination.

    Examples:
        Basic usage - iterate through pages:

        >>> from censys.platform import CensysSearch
        >>> search = CensysSearch()
        >>> paginator = search.search("services.port:443")
        >>> for page in paginator:
        ...     for hit in page:
        ...         print(hit.get("ip"))

        Get a single page without pagination:

        >>> paginator = search.search("services.port:443")
        >>> first_page = paginator.get_page()
        >>> for hit in first_page:
        ...     print(hit.get("ip"))

        Get a specific page by number:

        >>> third_page = paginator.get_page(page_number=3)

        Get all results in a single list:

        >>> all_results = paginator.get_all_results()
        >>> print(f"Found {len(all_results)} results")
        >>> print(f"Total available: {paginator.total}")

        Limit pages and specify fields:

        >>> paginator = search.search(
        ...     "services.port:443",
        ...     pages=2,
        ...     fields=["ip", "services.port"]
        ... )
    """

    # Total number of results (Set after first query)
    total: Optional[int] = None

    def __init__(
        self,
        api: "CensysSearch",
        query: str,
        page_size: int = 100,
        cursor: Optional[str] = None,
        pages: int = -1,
        fields: Optional[List[str]] = None,
        sort: Optional[Union[str, List[str]]] = None,
        **kwargs: Any,
    ):
        """Initialize ResultPaginator.

        Args:
            api: Parent Search API object.
            query: The query to be executed.
            page_size: Number of results per page. Defaults to 100.
            cursor: Optional cursor for pagination.
            pages: Number of pages to return. Defaults to -1 (all pages).
            fields: Optional fields to return.
            sort: Optional field(s) to sort on.
            **kwargs: Optional keyword args.
        """
        self.api = api
        self.query = query
        self.page_size = page_size
        self.cursor = cursor
        self.next_cursor: Optional[str] = None
        self.page = 0

        # If pages is <= 0, get all pages
        if pages <= 0:
            self.pages = float("inf")
        else:
            self.pages = pages

        self.fields = fields
        self.sort = sort
        self.extra_args = kwargs

    def __call__(self, page_size: Optional[int] = None) -> List[dict]:
        """Execute search and return the next page of results.

        Args:
            page_size: Override the number of results per page.

        Raises:
            StopIteration: When all requested pages have been received.

        Returns:
            List[dict]: One page of result hits.
        """
        if self.page > self.pages:
            raise StopIteration

        # Use the page_size parameter from the method call or the instance variable
        page_size = page_size if page_size is not None else self.page_size

        results = self.api.query(
            query=self.query,
            page_size=page_size,  # Pass page_size to the query method
            cursor=self.next_cursor or self.cursor,
            fields=self.fields,
            sort=self.sort,
            **self.extra_args,
        )

        self.page += 1
        result = results.get("result", {})
        self.total = result.get("total", 0)
        self.next_cursor = result.get("cursor")

        # If there are no more results or no cursor for next page
        if self.total == 0 or not self.next_cursor:
            self.pages = 0

        return result.get("hits", [])

    def __next__(self) -> List[dict]:
        """Get the next page of search results.

        Returns:
            List[dict]: One page of result hits.
        """
        return self.__call__()

    def __iter__(self) -> Iterator[List[dict]]:
        """Get iterator.

        Returns:
            Iterator: Returns self.
        """
        return self

    def get_page(
        self, page_number: int = 1, cursor: Optional[str] = None
    ) -> List[dict]:
        """Get a specific page of results without iterating.

        This method fetches a single page of results either by page number or cursor,
        without engaging the full pagination process.

        Args:
            page_number: The page number to retrieve (1-indexed). Defaults to 1.
            cursor: Optional cursor string to fetch a specific page directly.
                    If provided, page_number is ignored.

        Returns:
            List[dict]: The requested page of results.
        """
        # Save current state to restore later
        original_page = self.page
        original_cursor = self.next_cursor

        try:
            if cursor:
                # Use the provided cursor directly
                self.next_cursor = cursor
                self.page = 1  # Reset page counter
                return self.__call__()
            else:
                # Start from the beginning
                self.next_cursor = None
                self.page = 1

                # Skip pages until we reach the desired page
                for _ in range(page_number - 1):
                    # Warn once if skipping pages (since this uses quota)
                    if page_number > 1 and _ == 0:
                        warnings.warn(
                            "Warning: Skipping to a specific page still uses API quota for each page skipped. "
                            "Consider using get_all_results() if you need data from multiple pages."
                        )

                    self.__call__()

                # Return the requested page
                return self.__call__()
        finally:
            # Restore original state
            self.page = original_page
            self.next_cursor = original_cursor

    def get_all_results(self) -> List[dict]:
        """Collect all results into a single list.

        This method will iterate through all pages and combine the results.

        Returns:
            List[dict]: All results combined into a single list.
        """
        all_results = []

        # Save the current state to restore it after
        original_page = self.page
        original_cursor = self.next_cursor

        # Reset the paginator
        self.page = 1
        self.next_cursor = None

        try:
            for page in self:
                all_results.extend(page)
        finally:
            # Restore the original state if needed (for reuse)
            if original_page != 1:
                self.page = original_page
                self.next_cursor = original_cursor

        return all_results


class CensysSearch(CensysPlatformAPIv3):
    """Interacts with the Censys Platform Search API.

    Examples:
        Initialize the search client:

        >>> from censys.platform import CensysSearch
        >>> s = CensysSearch()

        Simple query - get raw API response:

        >>> results = s.query("services.port:443")
        >>> print(f"Found {results['result']['total']} results")
        >>> for hit in results['result']['hits']:
        ...     print(hit.get('ip'))

        Using the ResultPaginator for easier iteration:

        >>> paginator = s.search("services.port:443")
        >>> # Get just the first page
        >>> first_page = paginator.get_page()
        >>> # Iterate through all pages
        >>> for page in paginator:
        ...     for hit in page:
        ...         print(hit.get('ip'))
        >>> # Get all results at once
        >>> all_results = paginator.get_all_results()

        Aggregation example:

        >>> agg_results = s.aggregate("services.port:443", "services.service_name")
        >>> for bucket in agg_results['result']['buckets']:
        ...     print(f"{bucket['key']}: {bucket['count']}")
    """

    INDEX_NAME = "v3/global/search"

    def __init__(self, token: Optional[str] = None, **kwargs):
        """Inits CensysSearch.

        Args:
            token: Personal Access Token for Censys Platform API.
            **kwargs: Optional kwargs.
        """
        CensysPlatformAPIv3.__init__(self, token=token, **kwargs)

    def query(
        self,
        query: str,
        page_size: int = 100,
        cursor: Optional[str] = None,
        fields: Optional[List[str]] = None,
        sort: Optional[Union[str, List[str]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Search the global data.

        Args:
            query: The query to search for.
            page_size: Number of results per page. Defaults to 100.
            cursor: Optional cursor for pagination.
            fields: Optional fields to return.
            sort: Optional field(s) to sort on.
            **kwargs: Optional keyword args.

        Returns:
            Dict[str, Any]: The search result.
        """
        data = {"query": query, "page_size": page_size}
        if cursor:
            data["cursor"] = cursor
        if fields:
            data["fields"] = fields
        if sort:
            data["sort"] = sort

        return self._post(f"{self.INDEX_NAME}/query", data=data, **kwargs)

    def search(
        self,
        query: str,
        page_size: int = 100,
        cursor: Optional[str] = None,
        pages: int = -1,
        fields: Optional[List[str]] = None,
        sort: Optional[Union[str, List[str]]] = None,
        **kwargs: Any,
    ) -> ResultPaginator:
        """Search the global data and return a paginator for easy iteration.

        This method returns a ResultPaginator that handles pagination automatically.

        Args:
            query: The query to search for.
            page_size: Number of results per page. Defaults to 100.
            cursor: Optional cursor for pagination.
            pages: Number of pages to return. Defaults to -1 (all pages).
            fields: Optional fields to return.
            sort: Optional field(s) to sort on.
            **kwargs: Optional keyword args.

        Returns:
            ResultPaginator: Paginator for iterating through search results.
        """
        return ResultPaginator(
            self,
            query,
            page_size=page_size,
            cursor=cursor,
            pages=pages,
            fields=fields,
            sort=sort,
            **kwargs,
        )

    def aggregate(
        self,
        query: str,
        field: str,
        number_of_buckets: int = 50,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Aggregate search results by a field.

        Args:
            query: The query string.
            field: The field to aggregate on.
            number_of_buckets: Number of buckets to return. Defaults to 50.
            **kwargs: Optional keyword args.

        Returns:
            Dict[str, Any]: The aggregation result.
        """
        data = {"query": query, "field": field, "number_of_buckets": number_of_buckets}

        return self._post(f"{self.INDEX_NAME}/aggregate", data=data, **kwargs)
