"""Tests for the Censys Platform Search API with focus on complete coverage."""

from unittest.mock import patch

from censys.platform.v3.search import CensysSearch, ResultPaginator


def test_search_method_complete():
    """Test that the search method returns a ResultPaginator with all parameters."""
    with patch.object(CensysSearch, "__init__", return_value=None), patch(
        "censys.platform.v3.search.ResultPaginator"
    ) as mock_paginator:
        # Initialize the search class
        search = CensysSearch()
        search.INDEX_NAME = "test/index"

        # Call the search method with all parameters
        result: ResultPaginator = search.search(
            query="test query",
            page_size=50,
            cursor="test-cursor",
            pages=2,
            fields=["field1", "field2"],
            sort=["field1", "field2"],
            extra_param="extra_value",
        )

        # Verify ResultPaginator was created with all parameters
        mock_paginator.assert_called_once_with(
            search,
            "test query",
            page_size=50,
            cursor="test-cursor",
            pages=2,
            fields=["field1", "field2"],
            sort=["field1", "field2"],
            extra_param="extra_value",
        )

        # Ensure the result is what we got from ResultPaginator
        assert result == mock_paginator.return_value
