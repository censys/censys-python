import json
import unittest
from unittest.mock import patch

from .utils import (
    MockResponse,
    RESOURCE_PAGING_RESULTS,
    TEST_SUCCESS_CODE,
    TEST_TIMEOUT,
    BASE_URL,
)

from censys.asm.client import AsmClient
from censys.asm.events import Filters

EVENTS_URL = f"{BASE_URL}/logbook"
EVENTS_CURSOR_URL = f"{BASE_URL}/logbook-cursor"
EVENTS_RESOURCE_TYPE = "events"

TEST_CURSOR = "eyJmaWx0ZXIiOnt9LCJzdGFydCI6MH0"
TEST_NEXT_CURSOR = "eyJmaWx0ZXIiOnt9LCJzdGFydCI6MjA3MTJ9"
TEST_START_DATE = "2020-10-29T19:26:34.371Z"
TEST_START_ID = 20712


class EventsUnitTests(unittest.TestCase):
    """Unit tests for Events API."""

    def setUp(self):
        self.client = AsmClient()

    @patch("censys.base.requests.Session.post")
    def test_get_logbook_cursor_no_args(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, None)
        self.client.events.get_cursor()

        mock.assert_called_with(EVENTS_CURSOR_URL, params={}, timeout=TEST_TIMEOUT)

    @patch("censys.base.requests.Session.post")
    def test_get_logbook_cursor_with_start_date(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, None)
        self.client.events.get_cursor(start=TEST_START_DATE)

        mock.assert_called_with(
            EVENTS_CURSOR_URL,
            params={},
            timeout=TEST_TIMEOUT,
            data=json.dumps({"dateFrom": TEST_START_DATE}),
        )

    @patch("censys.base.requests.Session.post")
    def test_get_logbook_cursor_with_start_id(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, None)
        self.client.events.get_cursor(start=TEST_START_ID)

        mock.assert_called_with(
            EVENTS_CURSOR_URL,
            params={},
            timeout=TEST_TIMEOUT,
            data=json.dumps({"idFrom": TEST_START_ID}),
        )

    @patch("censys.base.requests.Session.post")
    def test_get_logbook_cursor_with_filters(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, None)
        filters = [Filters.HOST, Filters.DOMAIN]
        self.client.events.get_cursor(filters=filters)

        mock.assert_called_with(
            EVENTS_CURSOR_URL,
            params={},
            timeout=TEST_TIMEOUT,
            data=json.dumps({"filter": {"type": filters}}),
        )

    @patch("censys.base.requests.Session.post")
    def test_get_logbook_cursor_with_filters_and_start_date(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, None)
        filters = [Filters.HOST, Filters.HOST_CERT]
        self.client.events.get_cursor(start=TEST_START_DATE, filters=filters)

        mock.assert_called_with(
            EVENTS_CURSOR_URL,
            params={},
            timeout=TEST_TIMEOUT,
            data=json.dumps({"filter": {"type": filters}, "dateFrom": TEST_START_DATE}),
        )

    @patch("censys.base.requests.Session.post")
    def test_get_logbook_cursor_with_filters_and_start_id(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, None)
        filters = [Filters.HOST, Filters.HOST_CERT]
        self.client.events.get_cursor(start=TEST_START_ID, filters=filters)

        mock.assert_called_with(
            EVENTS_CURSOR_URL,
            params={},
            timeout=TEST_TIMEOUT,
            data=json.dumps({"filter": {"type": filters}, "idFrom": TEST_START_ID}),
        )

    @patch("censys.base.requests.Session.get")
    def test_get_all_events(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, EVENTS_RESOURCE_TYPE)
        events = self.client.events.get_events()
        res = list(events)

        assert RESOURCE_PAGING_RESULTS == res
        mock.assert_any_call(EVENTS_URL, params={"cursor": None}, timeout=TEST_TIMEOUT)
        mock.assert_any_call(
            EVENTS_URL, params={"cursor": TEST_NEXT_CURSOR}, timeout=TEST_TIMEOUT
        )

    @patch("censys.base.requests.Session.get")
    def test_get_events_with_cursor(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, EVENTS_RESOURCE_TYPE)
        events = self.client.events.get_events(TEST_CURSOR)
        res = list(events)

        assert RESOURCE_PAGING_RESULTS == res
        mock.assert_any_call(
            EVENTS_URL, params={"cursor": TEST_CURSOR}, timeout=TEST_TIMEOUT
        )
        mock.assert_any_call(
            EVENTS_URL, params={"cursor": TEST_NEXT_CURSOR}, timeout=TEST_TIMEOUT
        )


if __name__ == "__main__":
    unittest.main()
