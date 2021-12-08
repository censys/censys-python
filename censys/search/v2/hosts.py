"""Interact with the Censys Search Host API."""
from typing import List, Optional

from .api import CensysSearchAPIv2
from censys.common.types import Datetime
from censys.common.utils import format_rfc3339


class CensysHosts(CensysSearchAPIv2):
    """Interacts with the Hosts index.

    Examples:
        Inits Censys Hosts.

        >>> from censys.search import CensysHosts
        >>> h = CensysHosts()

        Simple host search.

        >>> for page in h.search("service.service_name: HTTP"):
        >>>     print(page)
        [
            {
            'services':
                [
                    {'service_name': 'HTTP', 'port': 80},
                    {'service_name': 'HTTP', 'port': 443}
                ],
            'ip': '1.0.0.0'
            },
            ...
        ]

        Fetch a specific host and its services

        >>> h.view("1.0.0.0")
        {
            'ip': '8.8.8.8',
            'services': [{}],
            ...
        }

        Simple host aggregate.

        >>> h.aggregate("service.service_name: HTTP", "services.port", num_buckets=5)
        {
            'total_omitted': 591527370,
            'buckets': [
                {'count': 56104072, 'key': '80'},
                {'count': 43527894, 'key': '443'},
                {'count': 23070429, 'key': '7547'},
                {'count': 12970769, 'key': '30005'},
                {'count': 12825150, 'key': '22'}
            ],
            'potential_deviation': 3985101,
            'field': 'services.port',
            'query': 'service.service_name: HTTP',
            'total': 172588754
        }

        Fetch a list of host names for the specified IP address.

        >>> h.view_host_names("1.1.1.1")
        ['one.one.one.one']

        Fetch a list of events for the specified IP address.

        >>> h.view_host_events("1.1.1.1")
        [{'timestamp': '2019-01-01T00:00:00.000Z'}]
    """

    INDEX_NAME = "hosts"
    """Name of Censys Index."""

    def view_host_names(self, ip_address: str) -> List[str]:
        """Fetches a list of host names for the specified IP address.

        Args:
            ip_address (str): The IP address of the requested host.

        Returns:
            List[str]: A list of host names.
        """
        return self._get(self.view_path + ip_address + "/names")["result"]["names"]

    def view_host_events(
        self,
        ip_address: str,
        start_time: Optional[Datetime] = None,
        end_time: Optional[Datetime] = None,
        per_page: Optional[int] = None,
        cursor: Optional[str] = None,
        reversed: Optional[bool] = None,
    ) -> List[dict]:
        """Fetches a list of events for the specified IP address.

        Args:
            ip_address (str): The IP address of the requested host.
            start_time (Datetime): Optional; An RFC3339 timestamp which represents
                the beginning chronological point-in-time (inclusive) from which events are returned.
            end_time (Datetime): Optional; An RFC3339 timestamp which represents
                the ending chronological point-in-time (exclusive) from which events are returned.
            per_page (int): Optional; The maximum number of hits to return in each response
                (minimum of 1, maximum of 50).
            cursor (str): Optional; Cursor token from the API response.
            reversed (bool): Optional; Reverse the order of the return events,
                that is, return events in reversed chronological order.

        Returns:
            List[dict]: A list of events.
        """
        args = {"per_page": per_page, "cursor": cursor, "reversed": reversed}
        if start_time:
            args["start_time"] = format_rfc3339(start_time)
        if end_time:
            args["end_time"] = format_rfc3339(end_time)

        return self._get(
            f"/v2/experimental/{self.INDEX_NAME}/{ip_address}/events", args
        )["result"]["events"]

    def list_hosts_with_tag(self, tag_id: str) -> List[str]:
        """Returns a list of hosts which are tagged with the specified tag.

        Args:
            tag_id (str): The ID of the tag.

        Returns:
            List[str]: A list of host IP addresses.
        """
        hosts = self._list_documents_with_tag(tag_id, "hosts", "hosts")
        return [host["ip"] for host in hosts]
