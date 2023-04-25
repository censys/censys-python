"""Interact with the Censys Risks API."""
from typing import List, Optional

from .api import CensysAsmAPI


class Risks(CensysAsmAPI):
    """Risks API class."""

    base_path = "/v2/risk"
    risk_instances_path = f"{base_path}-instances"
    risk_types_path = f"{base_path}-types"

    def get_risk_instances(
        self, include_events: Optional[bool] = None, accept: Optional[str] = None
    ) -> dict:
        """Retrieve risk instances.

        Args:
            include_events (bool): Optional; Whether to include events.
            accept (str): Optional; Accept header.

        Returns:
            dict: Risk instances result.
        """
        args = {"includeEvents": include_events}
        return self._get(
            self.risk_instances_path,
            args=args,
            headers={"Accept": accept} if accept else None,
        )

    def patch_risk_instances(self, data: dict) -> dict:
        """Patch risk instances.

        Args:
            data (dict): Risk instances data.

        Returns:
            dict: Risk instances result.
        """
        return self._patch(self.risk_instances_path, data=data)

    def search_risk_instances(self, data: dict, accept: Optional[str] = None) -> dict:
        """Search risk instances.

        Args:
            data (dict): Query data.
            accept (str): Optional; Accept header.

        Returns:
            dict: Risk instances result.
        """
        return self._post(
            f"{self.risk_instances_path}/search",
            data=data,
            headers={"Accept": accept} if accept else None,
        )

    def get_risk_instance(
        self, risk_instance_id: int, include_events: Optional[bool] = None
    ) -> dict:
        """Retrieve a risk instance.

        Args:
            risk_instance_id (int): Risk instance ID.
            include_events (bool): Optional; Whether to include events.

        Returns:
            dict: Risk instance result.
        """
        args = {"includeEvents": include_events}
        return self._get(f"{self.risk_instances_path}/{risk_instance_id}", args=args)

    def patch_risk_instance(self, risk_instance_id: int, data: dict) -> dict:
        """Patch a risk instance.

        Args:
            risk_instance_id (int): Risk instance ID.
            data (dict): Risk instance data.

        Returns:
            dict: Risk instance result.
        """
        return self._patch(f"{self.risk_instances_path}/{risk_instance_id}", data=data)

    def get_risk_types(
        self,
        sort: Optional[List[str]] = None,
        include_events: Optional[bool] = None,
        accept: Optional[str] = None,
    ) -> dict:
        """Retrieve risk types.

        Args:
            sort (list): Optional; Sort by field(s).
            include_events (bool): Optional; Whether to include events.
            accept (str): Optional; Accept header.

        Returns:
            dict: Risk types result.
        """
        args = {"sort": sort, "includeEvents": include_events}
        return self._get(
            self.risk_types_path,
            args=args,
            headers={"Accept": accept} if accept else None,
        )

    def get_risk_type(
        self, risk_type: str, include_events: Optional[bool] = None
    ) -> dict:
        """Retrieve a risk type.

        Args:
            risk_type (str): Risk type.
            include_events (bool): Optional; Whether to include events.

        Returns:
            dict: Risk type result.
        """
        args = {"includeEvents": include_events}
        return self._get(f"{self.risk_types_path}/{risk_type}", args=args)

    def patch_risk_type(self, risk_type: str, data: dict) -> dict:
        """Patch a risk type.

        Args:
            risk_type (str): Risk type.
            data (dict): Risk type data.

        Returns:
            dict: Risk type result.
        """
        return self._patch(f"{self.risk_types_path}/{risk_type}", data=data)
