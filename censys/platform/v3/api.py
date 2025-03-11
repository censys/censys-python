"""Base for interacting with the Censys Platform API."""

from typing import Any, Optional, Type

from requests.models import Response

from censys.common.base import CensysAPIBase
from censys.common.config import DEFAULT, get_config
from censys.common.exceptions import CensysExceptionMapper, CensysPlatformException


class CensysPlatformAPIv3(CensysAPIBase):
    """This class is the base class for the Platform API.

    Examples:
        >>> c = CensysPlatformAPIv3(token="your_platform_pat")
    """

    DEFAULT_URL: str = "https://api.platform.censys.io"
    """Default Platform API base URL."""
    INDEX_NAME: str = ""
    ASSET_NAME: str = ""
    API_VERSION: str = "v3"
    ASSET_VERSION: str = "v1"

    def __init__(
        self,
        token: Optional[str] = None,
        organization_id: Optional[str] = None,
        **kwargs,
    ):
        """Inits CensysPlatformAPIv3.

        Args:
            token (str, optional): Personal Access Token for Censys Platform API.
            organization_id (str, optional): Organization ID for Censys Platform API.
            **kwargs: Optional kwargs.

        Raises:
            ValueError: If no Personal Access Token is provided.
        """
        # For backward compatibility, but these aren't used
        api_id = kwargs.pop("api_id", None)
        api_secret = kwargs.pop("api_secret", None)

        if api_id or api_secret:
            import warnings

            warnings.warn(
                "api_id and api_secret are deprecated for Platform API. "
                "Please use token (PAT) instead.",
                DeprecationWarning,
                stacklevel=2,
            )

        url = kwargs.pop("url", self.DEFAULT_URL)
        CensysAPIBase.__init__(self, url=url, **kwargs)

        # Gets config file
        config = get_config()

        self.base_url = url
        self.organization_id = organization_id

        # Try to get Personal Access Token if not provided
        self._token = (
            token
            or kwargs.get("token")
            or config.get(DEFAULT, "platform_token", fallback=None)
        )
        self.organization_id = organization_id or config.get(
            DEFAULT, "platform_org_id", fallback=None
        )

        # Determine the Accept header based on asset type
        accept_header = "application/json"
        if self.ASSET_NAME:
            accept_header = f"application/vnd.censys.api.{self.API_VERSION}.{self.ASSET_NAME}.{self.ASSET_VERSION}+json"

        # Set up authentication headers using token
        if not self._token:
            raise ValueError("Personal Access Token is required for Platform API.")

        if not self.organization_id:
            raise ValueError("Organization ID is required for Platform API.")

        self._session.headers.update(
            {
                "Authorization": f"Bearer {self._token}",
                "X-Organization-ID": self.organization_id,
                "Accept": accept_header,
                "Content-Type": "application/json",
            }
        )

    def _get_exception_class(  # type: ignore
        self, res: Response
    ) -> Type[CensysPlatformException]:
        """Get the exception class for the response status code.

        Args:
            res (Response): Response object.

        Returns:
            Type[CensysPlatformException]: The exception class to raise.
        """
        return CensysExceptionMapper.exception_for_status_code(res.status_code)  # type: ignore

    def _get(self, endpoint: str, args: Optional[dict] = None, **kwargs: Any) -> dict:
        """Get data from a REST API endpoint.

        Args:
            endpoint (str): The endpoint to send the request to.
            args (dict, optional): The parameters to be sent in the request.
            **kwargs: Optional keyword args.

        Returns:
            dict: The returned data from the endpoint.
        """
        # Add organization_id to args if it exists and args is provided
        if self.organization_id and args is not None:
            args = {**args, "organization_id": self.organization_id}
        elif self.organization_id:
            args = {"organization_id": self.organization_id}
        return super()._get(endpoint, args, **kwargs)

    def view(self, resource_id: str, **kwargs: Any) -> dict:
        """View details of a specific resource.

        Args:
            resource_id (str): The resource ID to fetch.
            **kwargs: Optional keyword args.

        Returns:
            dict: The resource details.
        """
        # Organization ID is already in the headers, no need to add to query params
        params = kwargs.pop("params", {}) or {}
        return self._get(f"{self.INDEX_NAME}/{resource_id}", params=params, **kwargs)
