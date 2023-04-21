"""Base Exception for Censys API errors."""

from censys.common.response import CensysResponse


class CensysException(Exception):
    """Base Exception for Censys."""


class CensysCLIException(CensysException):
    """Base Exception for Censys CLI errors."""


class CensysAPIException(CensysException):
    """Base Exception for Censys API errors."""

    response: CensysResponse

    def __init__(self, response: CensysResponse) -> None:
        """Initialize the CensysAPIException.

        Args:
            response: The response from the request.
        """
        self.response = response
        super().__init__(response)


class CensysSearchAPIException(CensysAPIException):
    """Base Exception for Censys Search API errors."""


class CensysAsmAPIException(CensysAPIException):
    """Base Exception for Censys ASM API errors."""
