"""Interact with the Censys Platform WebProperty API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .api import CensysPlatformAPIv3
from censys.common.utils import format_rfc3339


class CensysWebProperties(CensysPlatformAPIv3):
    """Interacts with the Censys Platform WebProperty API.

    Examples:
        Inits Censys Platform WebProperties.

        >>> from censys.platform import CensysWebProperties
        >>> w = CensysWebProperties()

        Get webproperty details.

        >>> w.view("example.com:443")
        {
            "webproperty": {
                "name": "example.com:443",
                ...
            },
            ...
        }

        Get multiple webproperties.

        >>> w.bulk_view(["example.com:443", "example.org:443"])
        {
            "result": [
                {
                    "webproperty": {
                        "name": "example.com:443",
                        ...
                    }
                },
                {
                    "webproperty": {
                        "name": "example.org:443",
                        ...
                    }
                }
            ]
        }
    """

    INDEX_NAME = "v3/global/asset/webproperty"
    ASSET_NAME = "webproperty"

    def __init__(
        self,
        token: Optional[str] = None,
        organization_id: Optional[str] = None,
        **kwargs,
    ):
        """Inits CensysWebProperties.

        Args:
            token (str, optional): Personal Access Token for Censys Platform API.
            organization_id (str, optional): Organization ID to use for API requests.
            **kwargs: Optional kwargs.
        """
        CensysPlatformAPIv3.__init__(
            self, token=token, organization_id=organization_id, **kwargs
        )

    def view(  # type: ignore[override]
        self, webproperty_id: str, at_time: Optional[datetime] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Get a webproperty by ID.

        Args:
            webproperty_id (str): The webproperty ID to fetch.
            at_time (datetime, optional): Point in time to view the webproperty.
            **kwargs: Optional keyword args.

        Returns:
            Dict[str, Any]: The webproperty details.
        """
        params = {}
        if at_time:
            params["at_time"] = format_rfc3339(at_time)

        return self._get(f"{self.INDEX_NAME}/{webproperty_id}", params=params, **kwargs)

    def bulk_view(self, webproperty_ids: List[str], **kwargs: Any) -> Dict[str, Any]:
        """Get multiple webproperties by ID.

        Args:
            webproperty_ids (List[str]): The webproperty IDs to fetch.
            **kwargs: Optional keyword args.

        Returns:
            Dict[str, Any]: The webproperties details.
        """
        params = {"webproperty_ids": webproperty_ids}
        return self._get(self.INDEX_NAME, params=params, **kwargs)
