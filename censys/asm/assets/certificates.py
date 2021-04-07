"""
Interact with the Censys Certificate Assets API.
"""

from .assets import Assets


class CertificatesAssets(Assets):
    def __init__(self, *args, **kwargs):
        super().__init__("certificates", *args, **kwargs)
