"""Interact with the Censys Risks v1 API."""
from typing import Iterator, Optional

from ...common.deprecation import DeprecationDecorator
from ..api import CensysAsmAPI


class Risksv1(CensysAsmAPI):
    """Risks v1 API class."""

    base_path = "/v1/risks"

    @DeprecationDecorator(
        "The v1 Risks API is approaching deprecation and will be removed in the future."
    )
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Inits Risksv1.

        Args:
            api_key (str): Optional; The API Key provided by Censys.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(api_key, **kwargs)

    def get_risks(
        self,
        cloud: Optional[str] = None,
        environment: Optional[str] = None,
        include_accepted_risks: Optional[bool] = None,
        page_number: int = 1,
        page_size: int = 100,
    ) -> Iterator[dict]:
        """Retrieve risks.

        Returns a full list of all risks that affect any assets in the system,
        along with a count of assets affected by each risk.

        Args:
            cloud (str): The cloud to filter by.
            environment (str): The environment to filter by.
            include_accepted_risks (bool): Whether to include accepted risks.
            page_number (int): The page number to return.
            page_size (int): The number of items to return per page.

        Yields:
            dict: Host count result.
        """
        yield from self._get_page(
            self.base_path,
            page_number=page_number,
            page_size=page_size,
            args={
                "cloud": cloud,
                "environment": environment,
                "includeAcceptedRisks": include_accepted_risks,
            },
            keyword="data",
        )
