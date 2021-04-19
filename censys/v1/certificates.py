"""Interact with the Censys Search Certificate API."""
from typing import List

from .api import CensysSearchAPIv1


class CensysCertificates(CensysSearchAPIv1):
    """Interacts with the Certificates index.

    See CensysSearchAPIv1 for additional arguments.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """

    INDEX_NAME = "certificates"
    """Name of Censys Index."""
    MAX_PER_BULK_REQUEST = 50
    """Max number of bulk requests."""

    def __init__(self, *args, **kwargs):
        """Inits CensysCertificates."""
        super().__init__(self, *args, **kwargs)
        self.bulk_path = f"/bulk/{self.INDEX_NAME}"

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
