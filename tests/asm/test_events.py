import datetime
import unittest

import pytest
import responses
from pytest_mock import MockerFixture

from censys.asm.client import AsmClient
from censys.asm.logbook import Filters, Logbook

from .utils import (
    RESOURCE_PAGING_RESULTS,
    TEST_SUCCESS_CODE,
    TEST_TIMEOUT,
    V1_URL,
    MockResponse,
)

EVENTS_URL = f"{V1_URL}/logbook"
EVENTS_CURSOR_URL = f"{V1_URL}/logbook-cursor"
EVENTS_RESOURCE_TYPE = "events"

TEST_CURSOR = "eyJmaWx0ZXIiOnt9LCJzdGFydCI6MH0"
TEST_NEXT_CURSOR = "eyJmaWx0ZXIiOnt9LCJzdGFydCI6MjA3MTJ9"
TEST_START_DATE = "2020-10-29T19:26:34.371Z"
TEST_START_ID = 20712


@pytest.mark.parametrize(
    ("start", "expected"),
    [
        (datetime.datetime(2020, 10, 29, 19, 26, 34, 371000), {"dateFrom": "2020-10-29T19:26:34.371000Z"}),
        (
            datetime.datetime(
                2020, 10, 30, 0, 56, 34, 371000, tzinfo=datetime.timezone(datetime.timedelta(hours=5, minutes=30))
            ),
            {"dateFrom": "2020-10-29T19:26:34.371000Z"},
        ),
        (TEST_START_DATE, {"dateFrom": TEST_START_DATE}),
        (0, {"idFrom": 0}),
        (None, {}),
    ],
)
@responses.activate
def test_logbook_cursor_serializes_start(start, expected):
    body = {"filter": {"type": [Filters.HOST]}, **expected}
    responses.add(
        responses.POST,
        EVENTS_CURSOR_URL,
        json={"cursor": TEST_CURSOR},
        match=[responses.matchers.json_params_matcher(body)],
    )
    assert Logbook(api_key="test-api-key").get_cursor(start=start, filters=[Filters.HOST]) == TEST_CURSOR


class EventsUnitTests(unittest.TestCase):
    """Unit tests for Events API."""

    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker: MockerFixture):
        """Injects fixtures into the test case.

        Args:
            mocker (MockerFixture): pytest-mock fixture.
        """
        # Inject mocker fixture
        self.mocker = mocker

    """Unit tests for Host, Certificate, and Domain APIs."""

    def setUp(self):
        self.client = AsmClient()

    def test_get_logbook_cursor_no_args(self):
        # Mock
        mock_request = self.mocker.patch("censys.common.base.requests.Session.post")
        mock_request.return_value = MockResponse(TEST_SUCCESS_CODE, None)
        # Actual call
        self.client.events.get_cursor()
        # Assertions
        mock_request.assert_called_with(EVENTS_CURSOR_URL, params={}, timeout=TEST_TIMEOUT)

    def test_get_logbook_cursor_with_start_date(self):
        # Mock
        mock_request = self.mocker.patch("censys.common.base.requests.Session.post")
        mock_request.return_value = MockResponse(TEST_SUCCESS_CODE, None)
        # Actual call
        self.client.events.get_cursor(start=TEST_START_DATE)
        # Assertions
        mock_request.assert_called_with(
            EVENTS_CURSOR_URL,
            params={},
            timeout=TEST_TIMEOUT,
            json={"dateFrom": TEST_START_DATE},
        )

    def test_get_logbook_cursor_with_start_id(self):
        # Mock
        mock_request = self.mocker.patch("censys.common.base.requests.Session.post")
        mock_request.return_value = MockResponse(TEST_SUCCESS_CODE, None)
        # Actual call
        self.client.events.get_cursor(start=TEST_START_ID)
        # Assertions
        mock_request.assert_called_with(
            EVENTS_CURSOR_URL,
            params={},
            timeout=TEST_TIMEOUT,
            json={"idFrom": TEST_START_ID},
        )

    def test_get_logbook_cursor_with_filters(self):
        # Mock
        mock_request = self.mocker.patch("censys.common.base.requests.Session.post")
        mock_request.return_value = MockResponse(TEST_SUCCESS_CODE, None)
        filters = [Filters.HOST, Filters.DOMAIN]
        # Actual call
        self.client.events.get_cursor(filters=filters)
        # Assertions
        mock_request.assert_called_with(
            EVENTS_CURSOR_URL,
            params={},
            timeout=TEST_TIMEOUT,
            json={"filter": {"type": filters}},
        )

    def test_get_logbook_cursor_with_filters_and_start_date(self):
        # Mock
        mock_request = self.mocker.patch("censys.common.base.requests.Session.post")
        mock_request.return_value = MockResponse(TEST_SUCCESS_CODE, None)
        filters = [Filters.HOST, Filters.HOST_CERT]
        # Actual call
        self.client.events.get_cursor(start=TEST_START_DATE, filters=filters)
        # Assertion
        mock_request.assert_called_with(
            EVENTS_CURSOR_URL,
            params={},
            timeout=TEST_TIMEOUT,
            json={"filter": {"type": filters}, "dateFrom": TEST_START_DATE},
        )

    def test_get_logbook_cursor_with_filters_and_start_id(self):
        # Mock
        mock_request = self.mocker.patch("censys.common.base.requests.Session.post")
        mock_request.return_value = MockResponse(TEST_SUCCESS_CODE, None)
        filters = [Filters.HOST, Filters.HOST_CERT]
        # Actual call
        self.client.events.get_cursor(start=TEST_START_ID, filters=filters)
        # Assertions
        mock_request.assert_called_with(
            EVENTS_CURSOR_URL,
            params={},
            timeout=TEST_TIMEOUT,
            json={"filter": {"type": filters}, "idFrom": TEST_START_ID},
        )

    def test_get_all_events(self):
        # Mock
        mock_request = self.mocker.patch("censys.common.base.requests.Session.get")
        mock_request.return_value = MockResponse(TEST_SUCCESS_CODE, EVENTS_RESOURCE_TYPE)
        # Actual call
        events = self.client.events.get_events()
        res = list(events)
        # Assertions
        assert res == RESOURCE_PAGING_RESULTS
        mock_request.assert_any_call(EVENTS_URL, params={"cursor": None}, timeout=TEST_TIMEOUT)
        mock_request.assert_any_call(EVENTS_URL, params={"cursor": TEST_NEXT_CURSOR}, timeout=TEST_TIMEOUT)

    def test_get_events_with_cursor(self):
        # Mock
        mock_request = self.mocker.patch("censys.common.base.requests.Session.get")
        mock_request.return_value = MockResponse(TEST_SUCCESS_CODE, EVENTS_RESOURCE_TYPE)
        # Actual call
        events = self.client.events.get_events(TEST_CURSOR)
        res = list(events)
        # Assertions
        assert res == RESOURCE_PAGING_RESULTS
        mock_request.assert_any_call(EVENTS_URL, params={"cursor": TEST_CURSOR}, timeout=TEST_TIMEOUT)
        mock_request.assert_any_call(EVENTS_URL, params={"cursor": TEST_NEXT_CURSOR}, timeout=TEST_TIMEOUT)
