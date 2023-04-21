"""Base Client for interacting with the Censys APIs."""
import json
from typing import Optional

import backoff
import requests
from requests.sessions import Session

from .response import CensysResponse
from .version import __version__

DEFAULT_TIMEOUT: int = 30
"""Default API timeout."""

DEFAULT_USER_AGENT: str = f"censys-python/{__version__}"
"""Default API user agent."""

DEFAULT_MAX_RETRIES: int = 5
"""Default max number of API retries."""


class CensysBaseClient:
    """This is the base class for Censys API clients."""

    base_url: str
    """Base URL for the API."""

    timeout: int
    """Timeout for the API."""

    max_retries: int
    """Max number of retries for the API."""

    session: Session
    """Session for the API."""

    def __init__(
        self,
        base_url: str,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        user_agent: Optional[str] = None,
        proxies: Optional[dict] = None,
        cookies: Optional[dict] = None,
        **kwargs,
    ) -> None:
        """Initialize the CensysBaseClient.

        Args:
            base_url: Base URL for the API.
            timeout: Timeout for the API.
            max_retries: Max number of retries for the API.
            user_agent: User agent for the API.
            proxies: Proxies for the API.
            cookies: Cookies for the API.
            **kwargs: Additional keyword arguments.
        """
        self.base_url = base_url
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.max_retries = max_retries or DEFAULT_MAX_RETRIES

        # Initialize the session
        self.session = requests.Session()
        user_agents = [requests.utils.default_user_agent(), DEFAULT_USER_AGENT]
        if user_agent:
            user_agents.append(user_agent)
        self.session.headers.update(
            {
                "User-Agent": " ".join(user_agents),
                "Content-Type": "application/json",
            }
        )
        self.session.proxies.update(proxies or {})
        self.session.cookies.update(cookies or {})

    def __repr__(self) -> str:
        """Return the representation of the CensysBaseClient.

        Returns:
            str: Representation of the CensysBaseClient.
        """
        return f"{self.__class__.__name__}(base_url={self.base_url!r}, timeout={self.timeout!r}, max_retries={self.max_retries!r})"

    def __str__(self) -> str:
        """Return the string representation of the CensysBaseClient.

        Returns:
            str: String representation of the CensysBaseClient.
        """
        return self.__repr__()

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        **kwargs,
    ) -> CensysResponse:
        """Make a request to the Censys API.

        Args:
            method: HTTP method to use.
            path: Path to the endpoint.
            params: Parameters to send with the request.
            data: Data to send with the request.
            **kwargs: Additional keyword arguments.

        Returns:
            CensysResponse: Response from the API.
        """
        url = f"{self.base_url}{path}"
        response = self.session.request(
            method,
            url,
            params=params,
            data=json.dumps(data) if data else None,
            timeout=self.timeout,
            **kwargs,
        )
        return CensysResponse(response)

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=DEFAULT_MAX_RETRIES,
        max_time=DEFAULT_TIMEOUT,
    )
    def get(self, path: str, params: Optional[dict] = None, **kwargs) -> CensysResponse:
        """Make a GET request to the Censys API.

        Args:
            path: Path to the endpoint.
            params: Parameters to send with the request.
            **kwargs: Additional keyword arguments.

        Returns:
            CensysResponse: Response from the API.
        """
        return self._request("GET", path, params=params, **kwargs)

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=DEFAULT_MAX_RETRIES,
        max_time=DEFAULT_TIMEOUT,
    )
    def post(self, path: str, data: Optional[dict] = None, **kwargs) -> CensysResponse:
        """Make a POST request to the Censys API.

        Args:
            path: Path to the endpoint.
            data: Data to send with the request.
            **kwargs: Additional keyword arguments.

        Returns:
            CensysResponse: Response from the API.
        """
        return self._request("POST", path, data=data, **kwargs)

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=DEFAULT_MAX_RETRIES,
        max_time=DEFAULT_TIMEOUT,
    )
    def put(self, path: str, data: Optional[dict] = None, **kwargs) -> CensysResponse:
        """Make a PUT request to the Censys API.

        Args:
            path: Path to the endpoint.
            data: Data to send with the request.
            **kwargs: Additional keyword arguments.

        Returns:
            CensysResponse: Response from the API.
        """
        return self._request("PUT", path, data=data, **kwargs)

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=DEFAULT_MAX_RETRIES,
        max_time=DEFAULT_TIMEOUT,
    )
    def delete(self, path: str, **kwargs) -> CensysResponse:
        """Make a DELETE request to the Censys API.

        Args:
            path: Path to the endpoint.
            **kwargs: Additional keyword arguments.

        Returns:
            CensysResponse: Response from the API.
        """
        return self._request("DELETE", path, **kwargs)

    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=DEFAULT_MAX_RETRIES,
        max_time=DEFAULT_TIMEOUT,
    )
    def patch(self, path: str, data: Optional[dict] = None, **kwargs) -> CensysResponse:
        """Make a PATCH request to the Censys API.

        Args:
            path: Path to the endpoint.
            data: Data to send with the request.
            **kwargs: Additional keyword arguments.

        Returns:
            CensysResponse: Response from the API.
        """
        return self._request("PATCH", path, data=data, **kwargs)
