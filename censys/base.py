"""
Base for interacting with the Censys' API.

Classes:
    CensysAPIBase
    CensysIndex
"""

import os
import json
from typing import Type, Optional, Callable, Dict, List, Generator

import requests

from censys import __name__ as NAME, __version__ as VERSION
from censys.exceptions import (
    CensysException,
    CensysAPIException,
    CensysRateLimitExceededException,
    CensysNotFoundException,
    CensysUnauthorizedException,
    CensysJSONDecodeException,
)

Fields = Optional[List[str]]


class CensysAPIBase:

    DEFAULT_URL: str = "https://censys.io/api/v1"
    DEFAULT_TIMEOUT: int = 30
    DEFAULT_USER_AGENT: str = "%s/%s" % (NAME, VERSION)

    EXCEPTIONS: Dict[int, Type[CensysAPIException]] = {
        401: CensysUnauthorizedException,
        403: CensysUnauthorizedException,
        404: CensysNotFoundException,
        429: CensysRateLimitExceededException,
    }

    def __init__(
        self,
        api_id: Optional[str] = None,
        api_secret: Optional[str] = None,
        url: Optional[str] = None,
        timeout: Optional[int] = None,
        user_agent_identifier: Optional[str] = None,
    ):
        # Try to get credentials
        self.api_id = api_id or os.getenv("CENSYS_API_ID")
        self.api_secret = api_secret or os.getenv("CENSYS_API_SECRET")
        if not self.api_id or not self.api_secret:
            raise CensysException("No API ID or API secret configured.")

        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self._api_url = url or os.getenv("CENSYS_API_URL") or self.DEFAULT_URL

        # Create a session and sets credentials
        self._session = requests.Session()
        self._session.auth = (self.api_id, self.api_secret)
        self._session.headers.update(
            {
                "accept": "application/json, */8",
                "User-Agent": " ".join(
                    [
                        requests.utils.default_user_agent(),
                        user_agent_identifier or self.DEFAULT_USER_AGENT,
                    ]
                ),
            }
        )

        # Confirm setup
        self.account()

    def _get_exception_class(self, status_code: int) -> Type[CensysAPIException]:
        return self.EXCEPTIONS.get(status_code, CensysAPIException)

    def _make_call(
        self,
        method: Callable,
        endpoint: str,
        args: Optional[dict] = None,
        data: Optional[str] = None,
    ) -> dict:
        """
        wrapper functions for all our REST API calls
        checking for errors and decoding the response
        """
        if endpoint.startswith("/"):
            url = "".join((self._api_url, endpoint))
        else:
            url = "/".join((self._api_url, endpoint))

        request_kwargs = {
            "params": args or {},
            "timeout": self.timeout,
        }

        if data:
            data = json.dumps(data)
            request_kwargs["data"] = data

        res = method(url, **request_kwargs)

        if res.status_code == 200:
            return res.json()

        try:
            message = res.json()["error"]
            const = res.json().get("error_type", None)
        except ValueError:  # pragma: no cover
            message = (
                f"Response from {res.url} is not valid JSON and cannot be decoded."
            )
            raise CensysJSONDecodeException(
                status_code=res.status_code,
                message=message,
                body=res.text,
                const="badjson",
            )
        except KeyError:  # pragma: no cover
            message = None
            const = "unknown"
        censys_exception = self._get_exception_class(res.status_code)
        raise censys_exception(
            status_code=res.status_code,
            message=message,
            body=res.text,
            const=const,
        )

    def _get(self, endpoint: str, args: Optional[dict] = None) -> dict:
        return self._make_call(self._session.get, endpoint, args)

    def _post(self, endpoint: str, args: Optional[dict] = None, data=None) -> dict:
        return self._make_call(self._session.post, endpoint, args, data)

    def _delete(self, endpoint: str, args: Optional[dict] = None) -> dict:
        return self._make_call(self._session.delete, endpoint, args)  # pragma: no cover

    def account(self) -> dict:
        return self._get("account")


class CensysIndex(CensysAPIBase):

    INDEX_NAME: Optional[str] = None

    def __init__(self, *args, **kwargs):
        CensysAPIBase.__init__(self, *args, **kwargs)
        # Generate concrete paths to be called
        self.search_path = f"search/{self.INDEX_NAME}"
        self.view_path = f"view/{self.INDEX_NAME}"
        self.report_path = f"report/{self.INDEX_NAME}"

    def metadata(self, query: str):
        data = {"query": query, "page": 1, "fields": []}
        return self._post(self.search_path, data=data).get("metadata", {})

    def paged_search(
        self, query: str, fields: Fields = None, page: int = 1, flatten: bool = True,
    ):
        page = int(page)
        data = {
            "query": query,
            "page": page,
            "fields": fields or [],
            "flatten": flatten,
        }
        return self._post(self.search_path, data=data)

    def search(
        self,
        query: str,
        fields: Fields = None,
        page: int = 1,
        max_records: Optional[int] = None,
        flatten: bool = True,
    ) -> Generator[dict, None, None]:
        """returns iterator over all records that match the given query"""
        if fields is None:
            fields = []
        page = int(page)
        pages = float("inf")
        data = {"query": query, "page": page, "fields": fields, "flatten": flatten}

        count = 0
        while page <= pages:
            payload = self._post(self.search_path, data=data)
            pages = payload["metadata"]["pages"]
            page += 1
            data["page"] = page

            for result in payload["results"]:
                yield result
                count += 1
                if max_records and count >= max_records:
                    return

    def view(self, ip_address: str) -> dict:
        return self._get("/".join((self.view_path, ip_address)))

    def report(self, query: str, field: str, buckets: int = 50) -> dict:
        data = {"query": query, "field": field, "buckets": int(buckets)}
        return self._post(self.report_path, data=data)
