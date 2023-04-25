"""Interact with the Censys Search Certificate API."""
from typing import List

from .api import CensysSearchAPIv1
from censys.common.deprecation import DeprecationDecorator


class CensysCertificates(CensysSearchAPIv1):
    """Interacts with the Certificates index.

    See CensysSearchAPIv1 for additional arguments.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """

    DEFAULT_TIMEOUT: int = 90
    """Timeout for the certificates index"""
    DEFAULT_URL: str = "https://search.censys.io/api/v1"
    """Default Search API base URL."""
    INDEX_NAME = "certificates"
    """Name of Censys Index."""
    MAX_PER_BULK_REQUEST = 50
    """Max number of bulk requests."""
    bulk_path = f"/bulk/{INDEX_NAME}"

    @DeprecationDecorator(
        "The v1 Certificates API is deprecated and will be removed in the future."
    )
    def __init__(self, **kwargs):
        """Inits CensysCertificates.

        See CensysSearchAPIv1 for additional arguments.

        Args:
            **kwargs: Arbitrary keyword arguments.
        """
        CensysSearchAPIv1.__init__(
            self, timeout=kwargs.pop("timeout", self.DEFAULT_TIMEOUT), **kwargs
        )

    def bulk(self, fingerprints: List[str]) -> dict:
        """Requests bulk certificates.

        Args:
            fingerprints (List[str]): List of certificate SHA256 fingerprints.

        Returns:
            dict: Search results from an API query.
        """
        result = {}
        start = 0
        end = self.MAX_PER_BULK_REQUEST
        while start < len(fingerprints):
            data = {"fingerprints": fingerprints[start:end]}
            result.update(self._post(self.bulk_path, data=data))
            start = end
            end += self.MAX_PER_BULK_REQUEST

        return result
