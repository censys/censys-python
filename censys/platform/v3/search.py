"""Interact with the Censys Platform Search API."""

from typing import Any, Dict, List, Optional, Union

from .api import CensysPlatformAPIv3


class CensysSearch(CensysPlatformAPIv3):
    """Interacts with the Censys Platform Search API.

    Examples:
        Inits Censys Platform Search.

        >>> from censys.platform import CensysSearch
        >>> s = CensysSearch()

        Search for hosts.

        >>> s.query("services.port:443")
        {
            "result": {
                "hits": [
                    {
                        "host": {
                            "ip": "1.1.1.1",
                            ...
                        }
                    },
                    ...
                ],
                "total": 123456
            }
        }

        Aggregate host data.

        >>> s.aggregate("services.port:443", "services.service_name")
        {
            "result": {
                "buckets": [
                    {
                        "key": "HTTP",
                        "count": 12345
                    },
                    ...
                ]
            }
        }
    """

    INDEX_NAME = "v3/global/search"

    def __init__(self, token: Optional[str] = None, **kwargs):
        """Inits CensysSearch.

        Args:
            token (str, optional): Personal Access Token for Censys Platform API.
            **kwargs: Optional kwargs.
        """
        CensysPlatformAPIv3.__init__(self, token=token, **kwargs)

    def query(
        self,
        query: str,
        per_page: int = 100,
        cursor: Optional[str] = None,
        fields: Optional[List[str]] = None,
        sort: Optional[Union[str, List[str]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Search the global data.

        Args:
            query (str): The query to search for.
            per_page (int): Number of results per page. Defaults to 100.
            cursor (str, optional): Cursor for pagination.
            fields (List[str], optional): Fields to return.
            sort (Union[str, List[str]], optional): Field(s) to sort on.
            **kwargs: Optional keyword args.

        Returns:
            Dict[str, Any]: The search result.
        """
        data = {"q": query, "per_page": per_page}
        if cursor:
            data["cursor"] = cursor
        if fields:
            data["fields"] = fields
        if sort:
            data["sort"] = sort

        return self._post(f"{self.INDEX_NAME}/query", data=data, **kwargs)

    def aggregate(
        self,
        query: str,
        field: str,
        num_buckets: int = 50,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Aggregate the global data.

        Args:
            query (str): The query to search for.
            field (str): The field to aggregate on.
            num_buckets (int): Number of buckets to return. Defaults to 50.
            **kwargs: Optional keyword args.

        Returns:
            Dict[str, Any]: The aggregation result.
        """
        data = {"q": query, "field": field, "num_buckets": num_buckets}

        return self._post(f"{self.INDEX_NAME}/aggregate", data=data, **kwargs)
