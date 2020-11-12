"""
Client for interacting with the Censys ASM API.
"""

from typing import Optional

from censys.asm.seeds import Seeds
from censys.asm.assets import Assets
from censys.asm.events import Events


class AsmClient:
    """
    Client for interacting with the Censys Seeds, Assets, and Events API's.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.seeds = Seeds(api_key=api_key)
        self.hosts = Assets("hosts", api_key=api_key)
        self.certificates = Assets("certificates", api_key=api_key)
        self.domains = Assets("domains", api_key=api_key)
        self.events = Events(api_key=api_key)
