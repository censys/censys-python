"""
Interact with the Censys Host Assets API.
"""

from .assets import Assets


class HostsAssets(Assets):
    def __init__(self, *args, **kwargs):
        super().__init__("hosts", *args, **kwargs)
