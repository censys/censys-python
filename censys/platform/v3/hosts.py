"""Interact with the Censys Platform Host API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .api import CensysPlatformAPIv3


class CensysHosts(CensysPlatformAPIv3):
    """Interacts with the Censys Platform Host API.

    Examples:
        Inits Censys Platform Hosts.

        >>> from censys.platform import CensysHosts
        >>> h = CensysHosts()

        Get host details.

        >>> h.view("1.1.1.1")
        {
            "host": {
                "ip": "1.1.1.1",
                ...
            },
            ...
        }

        Get multiple hosts.

        >>> h.bulk_view(["1.1.1.1", "8.8.8.8"])
        {
            "result": [
                {
                    "host": {
                        "ip": "1.1.1.1",
                        ...
                    }
                },
                {
                    "host": {
                        "ip": "8.8.8.8",
                        ...
                    }
                }
            ]
        }

        Get host events timeline.

        >>> h.timeline("1.1.1.1")
        {
            "events": [
                {
                    "timestamp": "2023-01-01T00:00:00.000Z",
                    ...
                },
                ...
            ]
        }
    """

    INDEX_NAME = "v3/global/asset/host"
    ASSET_NAME = "host"

    def __init__(
        self,
        token: Optional[str] = None,
        organization_id: Optional[str] = None,
        **kwargs,
    ):
        """Inits CensysHosts.

        Args:
            token (str, optional): Personal Access Token for Censys Platform API.
            organization_id (str, optional): Organization ID for Censys Platform API.
            **kwargs: Optional kwargs.
        """
        CensysPlatformAPIv3.__init__(
            self, token=token, organization_id=organization_id, **kwargs
        )

    def view(  # type: ignore[override]
        self, host_id: str, at_time: Optional[datetime] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Get a host by ID.

        Args:
            host_id (str): The host ID to fetch.
            at_time (datetime, optional): Point in time to view the host.
            **kwargs: Optional keyword args.

        Returns:
            Dict[str, Any]: The host details.
        """
        params = {}
        if at_time:
            params["at_time"] = at_time.isoformat() + "Z"

        return self._get(f"{self.INDEX_NAME}/{host_id}", params=params, **kwargs)

    def bulk_view(self, host_ids: List[str], **kwargs: Any) -> Dict[str, Any]:
        """Get multiple hosts by ID.

        Args:
            host_ids (List[str]): The host IDs to fetch.
            **kwargs: Optional keyword args.

        Returns:
            Dict[str, Any]: The hosts details.
        """
        params = {"host_ids": host_ids}
        return self._get(self.INDEX_NAME, params=params, **kwargs)

    def timeline(
        self,
        host_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get the timeline of events for a host.

        Args:
            host_id (str): The host ID to fetch events for.
            start_time (datetime, optional): Start time for the timeline.
            end_time (datetime, optional): End time for the timeline.
            **kwargs: Optional keyword args.

        Returns:
            Dict[str, Any]: The host events.
        """
        params = {}
        if start_time:
            params["start_time"] = start_time.isoformat() + "Z"
        if end_time:
            params["end_time"] = end_time.isoformat() + "Z"

        return self._get(
            f"{self.INDEX_NAME}/{host_id}/timeline", params=params, **kwargs
        )
