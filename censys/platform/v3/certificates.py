"""Interact with the Censys Platform Certificate API."""

from typing import Any, Dict, List, Optional

from .api import CensysPlatformAPIv3


class CensysCertificates(CensysPlatformAPIv3):
    """Interacts with the Censys Platform Certificate API.

    Examples:
        Inits Censys Platform Certificates.

        >>> from censys.platform import CensysCertificates
        >>> c = CensysCertificates()

        Get certificate details.

        >>> c.view("a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1")
        {
            "certificate": {
                "fingerprint_sha256": "a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1",
                ...
            },
            ...
        }

        Get multiple certificates.

        >>> c.bulk_view(["a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1", "b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2"])
        {
            "result": [
                {
                    "certificate": {
                        "fingerprint_sha256": "a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1",
                        ...
                    }
                },
                {
                    "certificate": {
                        "fingerprint_sha256": "b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2",
                        ...
                    }
                }
            ]
        }
    """

    INDEX_NAME = "v3/global/asset/certificate"
    ASSET_NAME = "certificate"

    def __init__(
        self,
        token: Optional[str] = None,
        organization_id: Optional[str] = None,
        **kwargs,
    ):
        """Inits CensysCertificates.

        Args:
            token (str, optional): Personal Access Token for Censys Platform API.
            organization_id (str, optional): Organization ID to use for API requests.
            **kwargs: Optional kwargs.
        """
        CensysPlatformAPIv3.__init__(
            self, token=token, organization_id=organization_id, **kwargs
        )

    def view(self, certificate_id: str, **kwargs: Any) -> Dict[str, Any]:  # type: ignore[override]
        """Get a certificate by ID.

        Args:
            certificate_id (str): The certificate ID to fetch.
            **kwargs: Optional keyword args.

        Returns:
            Dict[str, Any]: The certificate details.
        """
        return self._get(f"{self.INDEX_NAME}/{certificate_id}", **kwargs)

    def bulk_view(self, certificate_ids: List[str], **kwargs: Any) -> Dict[str, Any]:
        """Get multiple certificates by ID.

        Args:
            certificate_ids (List[str]): The certificate IDs to fetch.
            **kwargs: Optional keyword args.

        Returns:
            Dict[str, Any]: The certificates details.
        """
        params = {"certificate_ids": certificate_ids}
        return self._get(self.INDEX_NAME, params=params, **kwargs)
