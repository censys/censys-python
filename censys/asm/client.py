"""
Interact with the Censys Seeds, Assets, and Logbook APIs.
"""

from typing import Optional

from censys.asm.seeds import Seeds
from censys.asm.assets import Assets
from censys.asm.events import Events


class AsmClient:
    """
    Client ASM API class.
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.seeds = Seeds(api_key, **kwargs)
        self.hosts = Assets("hosts", api_key, **kwargs)
        self.certificates = Assets("certificates", api_key, **kwargs)
        self.domains = Assets("domains", api_key, **kwargs)
        self.events = Events(api_key, **kwargs)
