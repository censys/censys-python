"""Interact with the Censys Certificate Assets API."""
from .assets import Assets


class CertificatesAssets(Assets):
    """Certificates Assets API class.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """

    def __init__(self, *args, **kwargs):
        """Inits CertificatesAssets."""
        super().__init__("certificates", *args, **kwargs)
