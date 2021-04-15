"""Interact with the Censys Clouds API."""
import datetime
from typing import Union

from .api import CensysAsmAPI


class Clouds(CensysAsmAPI):
    """Clouds API class."""

    base_path = "clouds"

    def get_host_counts(
        self,
        since: Union[str, datetime.date, datetime.datetime],
    ) -> dict:
        """Retrieve host counts by cloud.

        Hosts found after the date provided in the `since` parameter will be included in the new asset counts.

        Args:
            since ([str, datetime.date, datetime.datetime]): Date to include hosts from.

        Returns:
            dict: Host count result.
        """
        if isinstance(since, (datetime.date, datetime.datetime)):
            since = since.strftime("%Y-%m-%d")
        path = f"{self.base_path}/hostCounts/{since}"
        return self._get(path)
