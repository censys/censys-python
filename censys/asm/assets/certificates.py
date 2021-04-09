"""Interact with the Censys Certificate Assets API."""
from .assets import Assets


class CertificatesAssets(Assets):
    """Certificates Assets API class."""

    def __init__(self, *args, **kwargs):
        """Inits CertificatesAssets."""
        super().__init__("certificates", *args, **kwargs)
