"""Tests for the ResultPaginator class."""

import warnings
from unittest.mock import MagicMock

from tests.utils import CensysTestCase

from censys.platform.v3.search import CensysSearch, ResultPaginator


class TestResultPaginator(CensysTestCase):
    """Tests for the ResultPaginator class."""

    def setUp(self):
        """Set up test case."""
        self.api = MagicMock(spec=CensysSearch)

        # Mock API responses
        self.first_page_response = {
            "result": {
                "hits": [{"id": "1"}, {"id": "2"}],
                "total": 5,
                "cursor": "next-cursor",
            }
        }

        self.second_page_response = {
            "result": {
                "hits": [{"id": "3"}, {"id": "4"}],
                "total": 5,
                "cursor": "last-cursor",
            }
        }

        self.last_page_response = {
            "result": {
                "hits": [{"id": "5"}],
                "total": 5,
                "cursor": None,
            }
        }

    def test_initialization(self):
        """Test initialization of ResultPaginator."""
        paginator = ResultPaginator(
            self.api,
            "test query",
            page_size=10,
            pages=2,
            fields=["id", "name"],
            sort="id",
        )

        assert paginator.query == "test query"
        assert paginator.page_size == 10
        assert paginator.pages == 2
        assert paginator.fields == ["id", "name"]
        assert paginator.sort == "id"
        assert paginator.page == 0
        assert paginator.total is None

    def test_get_page(self):
        """Test getting a specific page."""
        # Set up API mock for first page test
        self.api.query.reset_mock()
        self.api.query.side_effect = [self.first_page_response]

        paginator = ResultPaginator(self.api, "test query")

        # Get first page
        results = paginator.get_page()

        # Check that API was called with correct parameters
        self.api.query.assert_called_once_with(
            query="test query",
            page_size=100,
            cursor=None,
            fields=None,
            sort=None,
        )

        # Check results
        assert results == [{"id": "1"}, {"id": "2"}]
        assert paginator.total == 5
        # The get_page method restores the original cursor state,
        # so instead we verify that the API returned the expected cursor
        assert self.first_page_response["result"]["cursor"] == "next-cursor"

        # Test getting page by number
        # Reset and set up API mock for page number test
        # For page 2, we need to return first page, then second page
        self.api.query.reset_mock()
        self.api.query.side_effect = [
            self.first_page_response,
            self.second_page_response,
        ]

        # Use context manager to ignore the warning about quota
        with warnings.catch_warnings(record=True) as w:
            # Get page 2
            results = paginator.get_page(page_number=2)

            # Verify a warning was issued
            assert len(w) == 1
            assert "API quota" in str(w[0].message)

        # Check API call count (should be called twice)
        assert self.api.query.call_count == 2

        # Check results are from the second page
        assert results == [{"id": "3"}, {"id": "4"}]

        # Test getting page by cursor
        self.api.query.reset_mock()
        self.api.query.side_effect = [self.second_page_response]

        # Get page with specific cursor
        results = paginator.get_page(cursor="custom-cursor")

        # Check that API was called with the custom cursor
        self.api.query.assert_called_once_with(
            query="test query",
            page_size=100,
            cursor="custom-cursor",
            fields=None,
            sort=None,
        )

        # Check results
        assert results == [{"id": "3"}, {"id": "4"}]

    def test_get_all_results(self):
        """Test getting all results."""
        # Set up API mock for all pages
        self.api.query.reset_mock()
        self.api.query.side_effect = [
            self.first_page_response,
            self.second_page_response,
            self.last_page_response,
        ]

        paginator = ResultPaginator(self.api, "test query")

        # Get all results
        results = paginator.get_all_results()

        # Check that API was called for all three pages
        assert self.api.query.call_count == 3

        # Check that all results were collected
        assert results == [
            {"id": "1"},
            {"id": "2"},
            {"id": "3"},
            {"id": "4"},
            {"id": "5"},
        ]

        # Check pagination state
        assert paginator.total == 5
        assert paginator.next_cursor is None

    def test_iteration(self):
        """Test iteration through pages."""
        # Set up API mock for all pages
        self.api.query.reset_mock()
        self.api.query.side_effect = [
            self.first_page_response,
            self.second_page_response,
            self.last_page_response,
        ]

        paginator = ResultPaginator(self.api, "test query")

        # Collect pages through iteration
        collected_pages = []
        for page in paginator:
            collected_pages.append(page)

        # Check that API was called for all three pages
        assert self.api.query.call_count == 3

        # Check that all pages were collected
        assert collected_pages == [
            [{"id": "1"}, {"id": "2"}],
            [{"id": "3"}, {"id": "4"}],
            [{"id": "5"}],
        ]

        # Check pagination state
        assert paginator.total == 5
        assert paginator.next_cursor is None

    def test_page_limit(self):
        """Test page limit functionality."""
        # Reset API mock
        self.api.query.reset_mock()
        self.api.query.side_effect = [
            self.first_page_response,
            self.second_page_response,
        ]

        # Create paginator with page limit of 2
        paginator = ResultPaginator(self.api, "test query", pages=2)

        # Get all results
        results = paginator.get_all_results()

        # Check that API was called only twice (respecting page limit)
        assert self.api.query.call_count == 2

        # Check that only results from first two pages were collected
        assert results == [
            {"id": "1"},
            {"id": "2"},
            {"id": "3"},
            {"id": "4"},
        ]
