"""Interact with the Censys Seeds, Assets, and Logbook APIs."""
from typing import Optional

from .assets import CertificatesAssets, DomainsAssets, HostsAssets, SubdomainsAssets
from .clouds import Clouds
from .events import Events
from .risks import Risksv1, Risksv2
from .seeds import Seeds


class AsmClient:
    """Client ASM API class."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Inits AsmClient.

        Args:
            api_key (str): Optional; The API Key provided by Censys.
            **kwargs: Arbitrary keyword arguments.
        """
        self.seeds = Seeds(api_key, **kwargs)
        self.hosts = HostsAssets(api_key, **kwargs)
        self.certificates = CertificatesAssets(api_key, **kwargs)
        self.domains = DomainsAssets(api_key, **kwargs)
        self.events = Events(api_key, **kwargs)
        self.clouds = Clouds(api_key, **kwargs)
        # Risks v1 is approaching deprecation.
        self.risks_v1 = Risksv1(api_key, **kwargs)
        self.risks_v2 = Risksv2(api_key, **kwargs)
        self.risks = self.risks_v2

        # Save the arguments for parameterized client usage
        self.__api_kwargs = kwargs

    def get_subdomains(self, domain: str):
        """Get an API instance for subdomains of the parent domain.

        Args:
            domain: (str): Parent domain to access.

        Returns:
            SubdomainsAssets: A Subdomains Assets API instance .
        """
        return SubdomainsAssets(domain, self.domains._api_key, **self.__api_kwargs)
