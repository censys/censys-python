"""Interact with the Censys Inventory Search API."""
import warnings
from typing import List, Optional

from .api import CensysAsmAPI


class InventorySearch(CensysAsmAPI):
    """Inventory Search API class."""

    base_path = "/inventory/v1"

    def search(
        self,
        workspaces: Optional[List[str]] = None,
        query: Optional[str] = None,
        page_size: Optional[int] = None,
        cursor: Optional[str] = None,
        sort: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
    ) -> dict:
        """Search inventory data.

        Args:
            workspaces (List[str], optional): List of workspace IDs to search. Deprecated. The workspace associated with `CENSYS-API-KEY` will be used automatically.
            query (str, optional): Query string.
            page_size (int, optional): Number of results to return. Defaults to 50.
            cursor (str, optional): Cursor to start search from.
            sort (List[str], optional): List of fields to sort by.
            fields (List[str], optional): List of fields to return.

        Returns:
            dict: Inventory search results.
        """
        if workspaces is None:
            workspaces = [self.get_workspace_id()]
        else:
            warnings.warn(
                "The field 'workspaces' is being deprecated. The workspace associated with `CENSYS-API-KEY` will be used automatically.",
                category=DeprecationWarning,
                stacklevel=2,
            )
        if page_size is None:
            page_size = 50

        args = {
            "workspaces": workspaces,
            "pageSize": page_size,
        }

        if query:
            args["query"] = query
        if cursor:
            args["cursor"] = cursor
        if sort:
            args["sort"] = sort
        if fields:
            args["fields"] = fields

        return self._get(self.base_path, args=args)

    def aggregate(
        self,
        workspaces: List[str],
        query: Optional[str] = None,
        aggregation: Optional[dict] = None,
    ) -> dict:
        """Aggregate inventory data.

        Args:
            workspaces (List[str]): List of workspace IDs to search.
            query (str, optional): Query string.
            aggregation (dict, optional): Aggregation object.

        Returns:
            dict: Inventory aggregation results.
        """
        body = {
            "workspaces": workspaces,
            "query": query,
            "aggregation": aggregation,
        }

        return self._post(f"{self.base_path}/aggregate", data=body)

    def fields(self, fields: Optional[List[str]] = None) -> dict:
        """List inventory fields.

        If no fields are specified, all fields will be returned.

        Args:
            fields (List[str], optional): List of fields to return.

        Returns:
            dict: Inventory field results.
        """
        args = {"fields": fields}

        return self._get(f"{self.base_path}/fields", args=args)


Inventory = InventorySearch
