"""Interact with the Censys Domain Assets API."""
from .assets import Assets


class DomainsAssets(Assets):
    """Domains Assets API class.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """

    def __init__(self, *args, **kwargs):
        """Inits DomainsAssets."""
        super().__init__("domains", *args, **kwargs)

    # TODO: Subdomains
