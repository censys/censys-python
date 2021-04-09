"""Interact with the Censys Seeds, Assets, and Logbook APIs."""
from typing import Optional

from .seeds import Seeds
from .assets import CertificatesAssets, DomainsAssets, HostsAssets
from .events import Events


class AsmClient:
    """Client ASM API class."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Inits AsmClient.

        Args:
            api_key (str, optional): The API Key provided by Censys.
        """
        self.seeds = Seeds(api_key, **kwargs)
        self.hosts = HostsAssets(api_key, **kwargs)
        self.certificates = CertificatesAssets(api_key, **kwargs)
        self.domains = DomainsAssets(api_key, **kwargs)
        self.events = Events(api_key, **kwargs)
