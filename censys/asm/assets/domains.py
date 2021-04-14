"""Interact with the Censys Domain Assets API."""
from .assets import Assets

from typing import Generator, Optional


class DomainsAssets(Assets):
    """Domains Assets API class.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """

    def __init__(self, *args, **kwargs):
        """Inits DomainsAssets."""
        super().__init__("domains", *args, **kwargs)

    def get_subdomains(
        self, domain: str, page_number: int = 1, page_size: Optional[int] = None
    ) -> Generator[dict, None, None]:
        """List all subdomains of the parent domain.

        Args:
            domain: (str): Domain to get subdomains from.
            page_number (int): Optional; Page number to begin at when searching.
            page_size (int): Optional; Page size for retrieving assets.

        Returns:
            generator: Asset search results.
        """
        return self._get_page(
            f"{self.base_path}/{domain}/subdomains",
            page_number=page_number,
            page_size=page_size,
        )
