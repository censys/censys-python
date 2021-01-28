"""
Base for interacting with the Censys API's.
"""

import os
import json
import warnings
from functools import wraps
from typing import Any, Callable, List, Optional, Type

import backoff
import requests
from requests.models import Response

from censys import __name__ as NAME
from censys import __version__ as VERSION
from censys.exceptions import (
    CensysAPIException,
    CensysException,
    CensysJSONDecodeException,
    CensysRateLimitExceededException,
    CensysTooManyRequestsException,
)

Fields = Optional[List[str]]


# Wrapper to make max_retries configurable at runtime
def _backoff_wrapper(method: Callable):
    @wraps(method)
    def _wrapper(self, *args, **kwargs):
        @backoff.on_exception(
            backoff.expo,
            (
                CensysRateLimitExceededException,
                CensysTooManyRequestsException,
            ),
            max_tries=self.max_retries,
        )
        def _impl():
            return method(self, *args, *kwargs)

        return _impl()

    return _wrapper


class CensysAPIBase:
    """
    This is the base class for API queries.

    Args:
        url (str, optional): The URL to make API requests.
        timeout (int, optional): Timeout for API requests in seconds.
        user_agent (str, optional): Override User-Agent string.
        proxies (dict, optional): Configure HTTP proxies.

    Raises:
        CensysException: Base Exception Class for the Censys API.
    """

    DEFAULT_TIMEOUT: int = 30
    """Default API timeout."""
    DEFAULT_USER_AGENT: str = "%s/%s" % (NAME, VERSION)
    """Default API user agent."""
    DEFAULT_MAX_RETRIES: int = 10
    """Default max number of API retries."""

    def __init__(self, url: Optional[str] = None, **kwargs):
        # Get common request settings
        self.timeout = kwargs.get("timeout") or self.DEFAULT_TIMEOUT
        self.max_retries = kwargs.get("max_retries") or self.DEFAULT_MAX_RETRIES
        self._api_url = url or os.getenv("CENSYS_API_URL")

        if not self._api_url:
            raise CensysException("No API url configured.")

        # Create a session and set credentials
        self._session = requests.Session()
        proxies = kwargs.get("proxies")
        if proxies:
            if "http" in proxies.keys():
                warnings.warn("HTTP proxies will not be used.")
                proxies.pop("http", None)
            self._session.proxies = proxies
        self._session.headers.update(
            {
                "accept": "application/json, */8",
                "User-Agent": " ".join(
                    [
                        requests.utils.default_user_agent(),
                        kwargs.get("user_agent")
                        or kwargs.get("user_agent_identifier")
                        or self.DEFAULT_USER_AGENT,
                    ]
                ),
            }
        )

    @staticmethod
    def _get_exception_class(_: Response) -> Type[CensysAPIException]:
        """
        Maps HTTP status code or ASM error code to exception.
        Must be implemented by child class.

        Args:
            _ (Response): HTTP requests response object.

        Returns:
            Type[CensysAPIException]: Exception to raise.
        """
        return CensysAPIException

    @_backoff_wrapper
    def _make_call(
        self,
        method: Callable,
        endpoint: str,
        args: Optional[dict] = None,
        data: Optional[Any] = None,
    ) -> dict:
        """
        Wrapper functions for all our REST API calls checking for errors
        and decoding the responses.

        Args:
            method (Callable): Method to send HTTP request.
            endpoint (str): The path of API endpoint.
            args (dict, optional): URL args that are mapped to params.
            data (Any, optional): JSON data to serialize with request.

        Raises:
            CensysJSONDecodeException: The response is not valid JSON.

        Returns:
            dict: Results from an API request.
        """

        if endpoint.startswith("/"):
            url = f"{self._api_url}{endpoint}"
        else:
            url = f"{self._api_url}/{endpoint}"

        request_kwargs = {
            "params": args or {},
            "timeout": self.timeout,
        }

        if data:
            data = json.dumps(data)
            request_kwargs["data"] = data

        res = method(url, **request_kwargs)

        if res.status_code == 200:
            # Check for a returned json body
            try:
                return res.json()
            # Successful request returned no json body in response
            except ValueError:
                return {}

        try:
            json_data = res.json()
            message = json_data.get("error") or json_data["message"]
            const = json_data.get("error_type", None)
            error_code = json_data.get("errorCode", None)
            details = json_data.get("details", None)
        except (ValueError, json.decoder.JSONDecodeError) as error:  # pragma: no cover
            message = (
                f"Response from {res.url} is not valid JSON and cannot be decoded."
            )
            raise CensysJSONDecodeException(
                status_code=res.status_code,
                message=message,
                body=res.text,
                const="badjson",
            ) from error
        except KeyError:  # pragma: no cover
            message = None
            const = "unknown"
            details = "unknown"
            error_code = "unknown"

        censys_exception = self._get_exception_class(res)
        raise censys_exception(
            status_code=res.status_code,
            body=res.text,
            const=const,
            message=message,
            error_code=error_code,
            details=details,
        )

    def _get(self, endpoint: str, args: Optional[dict] = None) -> dict:
        return self._make_call(self._session.get, endpoint, args)

    def _post(
        self, endpoint: str, args: Optional[dict] = None, data: Optional[dict] = None
    ) -> dict:
        return self._make_call(self._session.post, endpoint, args, data)

    def _put(
        self, endpoint: str, args: Optional[dict] = None, data: Optional[dict] = None
    ) -> dict:
        return self._make_call(
            self._session.put, endpoint, args, data
        )  # pragma: no cover

    def _delete(self, endpoint: str, args: Optional[dict] = None) -> dict:
        return self._make_call(self._session.delete, endpoint, args)  # pragma: no cover
