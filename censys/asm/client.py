"""
Base for interacting with the Censys Search API.
"""
# pylint: disable=too-many-arguments
import os

from censys.base import CensysAPIBase
from censys.asm.seeds import Seeds
from censys.asm.assets import Assets
from censys.asm.events import Events
from censys.config import get_config, DEFAULT

from math import inf
from typing import Type, Dict, Generator
from requests.models import Response
from censys.exceptions import *


class CensysAsmAPI(CensysAPIBase):
    """
    This is the base class for ASM's Seeds, Assets, and Events classes
    """

    DEFAULT_URL: str = "https://app.censys.io/api/v1"
    """Default ASM API base URL."""
    EXCEPTIONS: Dict[int, Type[CensysAPIException]] = {
        10000: CensysMissingApiKeyException,
        10008: CensysInvalidRequestException,
        10002: CensysInvalidAuthTokenException,
        10001: CensysInvalidAPIKeyException,
        10039: CensysTooManyRequestsException,
        10029: CensysAppDownForMaintenanceException,
        10007: CensysInvalidSeedDataException,
        10017: CensysAssociatedAssetsThresholdWarningException,
        10016: CensysTooManyInputNodesException,
        10014: CensysSeedNotFoundException,
        10015: CensysNotASeedException,
        10013: CensysNeedConfirmationToRemoveParentSeedsException,
        10012: CensysCannotRemoveNonExistentSeedsException,
        10011: CensysCannotRemoveNonSeedsException,
        10038: CensysInvalidSeedTypeException,
        10040: CensysInvalidLogbookCursorException,
        10051: CensysPageNumberOutOfRangeException,
        10050: CensysInvalidPageSizeException,
        10018: CensysHostNotFoundException,
        10021: CensysInvalidIPv4AddressException,
        10054: CensysInvalidCommentException,
        10055: CensysCommentNotFoundException,
        10037: CensysInvalidColorException,
        10025: CensysTagHasTrailingOrLeadingWhitespaceException,
        10026: CensysTagIsEmptyStringException,
        10027: CensysTagLabelsDifferOnlyInCasingException,
        10028: CensysTagLabelTooLongException,
        10034: CensysTagColorTooLongException,
        10035: CensysCannotCreateTagWithNewColorException,
        10036: CensysTagColorHasTrailingOrLeadingWhitespaceException,
        10020: CensysCertificateNotFoundException,
        10019: CensysDomainNotFoundException
    }
    """Map of status code to Exception."""

    def __init__(
            self, api_key: Optional[str] = None,
            url: Optional[str] = DEFAULT_URL,
            **kwargs
    ):
        CensysAPIBase.__init__(self, url, **kwargs)

        # Gets config file
        config = get_config()

        # Try to get credentials
        self._api_key = (
            api_key or os.getenv("CENSYS_API_KEY") or config.get(DEFAULT, "api_key")
        )

        if not self._api_key:
            raise CensysAsmException("No API key configured.")

        self._session.headers.update({
            'Content-Type': 'application/json',
            'Censys-Api-Key': self._api_key
        })

        # Instantiate endpoint handlers
        self.seeds = Seeds(self)
        self.hosts = Assets(self, 'hosts')
        self.certificates = Assets(self, 'certificates')
        self.domains = Assets(self, 'domains')
        self.events = Events(self)

    def _get_exception_class(self, res: Response) -> Type[CensysAsmException]:
        return self.EXCEPTIONS.get(res.json()['errorCode'], CensysAsmException)

    def _get_page(
            self, path: str, page_number: Optional[int] = 1, page_size: Optional[int] = None
    ) -> Generator[dict, None, None]:
        """
        Fetches paginated ASM resource API results.

        Args:
            path (str): The API url endpoint.
            page_number (int, optional): The page number to begin at when returning results.
            page_size (int, optional): The number of results to return per HTTP request

        Returns:
            generator: The resource result set returned.
        """

        total_pages = inf

        while page_number <= total_pages:
            args = {
                'pageNumber': page_number,
                'pageSize': page_size or 500
            }

            res = self._get(path, args=args)
            page_number = int(res['pageNumber']) + 1
            total_pages = int(res['totalPages'])

            if 'comments' in path:
                for comment in res['comments']:
                    yield comment
            else:
                for asset in res['assets']:
                    yield asset

    def _get_logbook_page(self, path: str, args: Optional[dict] = None) -> Generator[dict, None, None]:
        """
        Fetches paginated ASM logbook API events.

        Args:
            path (str): The API url endpoint.
            args (dict, optional): URL args that are mapped to params (cursor).

        Returns:
            generator: The event result set returned.
        """

        end_of_events = False

        while not end_of_events:
            res = self._get(path, args=args)
            end_of_events = res['endOfEvents']

            for event in res['events']:
                yield event
