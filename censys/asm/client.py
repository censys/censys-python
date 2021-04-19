"""Interact with the Censys Seeds, Assets, and Logbook APIs."""
from typing import Optional

from .assets import CertificatesAssets, DomainsAssets, HostsAssets
from .clouds import Clouds
from .events import Events
from .seeds import Seeds


class AsmClient:
    """Client ASM API class.

    Args:
        api_key (str): Optional; The API Key provided by Censys.
        **kwargs: Arbitrary keyword arguments.
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """Inits AsmClient."""
        self.seeds = Seeds(api_key, **kwargs)
        self.hosts = HostsAssets(api_key, **kwargs)
        self.certificates = CertificatesAssets(api_key, **kwargs)
        self.domains = DomainsAssets(api_key, **kwargs)
        self.events = Events(api_key, **kwargs)
        self.clouds = Clouds(api_key, **kwargs)
