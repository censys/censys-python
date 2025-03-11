"""Interact with all Censys Platform APIs through a unified client."""

from typing import Optional

from .v3 import CensysCertificates, CensysHosts, CensysSearch, CensysWebProperties


class CensysPlatformClient:
    """Client for interacting with all Censys Platform APIs.

    Examples:
        Initialize the Platform client:

        >>> from censys.platform import CensysPlatformClient
        >>> client = CensysPlatformClient()

        Access all Platform API resources through a single client:

        >>> hosts = client.hosts                # CensysHosts instance
        >>> certs = client.certificates         # CensysCertificates instance
        >>> web = client.webproperties          # CensysWebProperties instance
        >>> search = client.search              # CensysSearch instance

        Perform operations with the client:

        >>> host_results = client.hosts.search("host.services: (port = 22 and protocol = 'SSH')")
        >>> cert_results = client.certificates.search("certificate.issuer.common_name: *Google*")
    """

    hosts: CensysHosts
    certificates: CensysCertificates
    webproperties: CensysWebProperties
    search: CensysSearch

    def __init__(
        self,
        token: Optional[str] = None,
        organization_id: Optional[str] = None,
        **kwargs,
    ):
        """Initialize the CensysPlatformClient.

        Args:
            token (str, optional): Personal Access Token for the Censys Platform API.
            organization_id (str, optional): Organization ID for the Censys Platform API.
            **kwargs: Optional keyword arguments to pass to the API clients.
        """
        self.hosts = CensysHosts(token=token, organization_id=organization_id, **kwargs)
        self.certificates = CensysCertificates(
            token=token, organization_id=organization_id, **kwargs
        )
        self.webproperties = CensysWebProperties(
            token=token, organization_id=organization_id, **kwargs
        )
        self.search = CensysSearch(
            token=token, organization_id=organization_id, **kwargs
        )
