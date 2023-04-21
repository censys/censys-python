"""Base response class for Censys API responses."""
from typing import Any, Dict, Optional, Union

from requests import JSONDecodeError, Response

from censys.exceptions import CensysException


class CensysResponse:
    """Base response class for Censys API responses."""

    _response: Optional[Response]
    _json: Optional[Dict[str, Any]]
    _error: Optional[str]

    def __init__(self, request_response: Optional[Response] = None) -> None:
        """Initialize the CensysResponse.

        Args:
            request_response: The response from the request.

        Raises:
            CensysException: If no response is provided.
        """
        if request_response is None:
            raise CensysException("No response provided.")
        self._response = request_response
        try:
            self._json = self._response.json()
        except JSONDecodeError as error:
            self._json = None
            self._error = str(error)

    def __repr__(self) -> str:
        """Return the representation of the CensysResponse.

        Returns:
            str: The representation of the CensysResponse.
        """
        return f"<CensysResponse: {self._response}>"

    def __str__(self) -> str:
        """Return the string representation of the CensysResponse.

        Returns:
            str: The string representation of the CensysResponse.
        """
        return self._response.text

    def __bool__(self) -> bool:
        """Return whether the CensysResponse is truthy.

        Returns:
            bool: Whether the CensysResponse is truthy.
        """
        return bool(self._response)

    def __len__(self) -> int:
        """Return the length of the CensysResponse.

        Returns:
            int: The length of the CensysResponse.
        """
        return len(self._response)

    def __getitem__(self, key: Union[int, str]) -> Any:
        """Return the item at the given key.

        Args:
            key: The key to get the item at.

        Returns:
            Any: The item at the given key.
        """
        return self._response[key]

    def __iter__(self) -> Any:
        """Return an iterator over the CensysResponse.

        Returns:
            Any: An iterator over the CensysResponse.
        """
        return iter(self._response)
