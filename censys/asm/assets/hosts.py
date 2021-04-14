"""Interact with the Censys Host Assets API."""
from .assets import Assets


class HostsAssets(Assets):
    """Hosts Assets API class.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """

    def __init__(self, *args, **kwargs):
        """Inits HostsAssets."""
        super().__init__("hosts", *args, **kwargs)
