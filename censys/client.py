"""Interact with all Search APIs."""
from .deprecation import DeprecationDecorator
from .v1 import CensysCertificates, CensysData, CensysIPv4, CensysWebsites
from .v2 import CensysHosts


class SearchClient:
    """Client for interacting with all Search APIs.

    Examples:
        Inits SearchClient.

        >>> from censys import SearchClient
        >>> c = SearchClient()

        Access both v1 and v2 indexes.

        >>> certs = c.v1.certificates # CensysCertificates()
        >>> data = c.v1.data # CensysData()
        >>> ipv4 = c.v1.ipv4 # CensysIPv4()
        >>> websites = c.v1.websites # CensysWebsites()
        >>> hosts = c.v2.hosts # CensysHosts()

        All indexes are passed all *args and **kwargs that are provided.
    """

    class _V1:
        """Class for v1 Search APIs."""

        @DeprecationDecorator(
            "The v1 Search API is deprecated and will be removed in the future."
        )
        def __init__(self, *args, **kwargs):
            """Inits V1."""
            self.certificates = CensysCertificates(*args, **kwargs)
            self.data = CensysData(*args, **kwargs)
            self.ipv4 = CensysIPv4(*args, **kwargs)
            self.websites = CensysWebsites(*args, **kwargs)

    class _V2:
        """Class for v2 Search APIs."""

        def __init__(self, *args, **kwargs):
            """Inits V2."""
            self.hosts = CensysHosts(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        """Inits SearchClient."""
        # Backwards compatability
        if len(args) == 2:
            kwargs["api_id"] = args[0]
            kwargs["api_secret"] = args[1]

        self.v1 = self._V1(**kwargs)
        self.v2 = self._V2(**kwargs)
