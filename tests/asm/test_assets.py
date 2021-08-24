import unittest
from unittest.mock import patch

import pytest
from parameterized import parameterized_class

from .utils import (
    BASE_URL,
    RESOURCE_PAGING_RESULTS,
    TEST_SUCCESS_CODE,
    TEST_TIMEOUT,
    MockResponse,
)
from censys.asm.client import AsmClient
from censys.common.exceptions import CensysInvalidColorException

ASSETS_URL = f"{BASE_URL}/assets"
ASSET_TYPE = "assets"
COMMENT_TYPE = "comments"

TEST_PAGE_NUMBER = 2
TEST_PAGE_SIZE = 2

TEST_COMMENT_ID = 3
TEST_COMMENT_TEXT = "This is a test comment"
TEST_TAG_NAME = "asset-test-tag"
TEST_TAG_COLOR = "#4287f5"
TEST_INVALID_TAG_COLOR = "4287f5"


@parameterized_class(
    ("asset_type", "test_asset_id"),
    [
        ("hosts", "3.12.122.3"),
        (
            "certificates",
            "0006afc1ddc8431aa57c812adf028ab4f168b25bf5f06e94af86edbafa88dfe0",
        ),
        ("domains", "amazonaws.com"),
    ],
)
class AssetsUnitTest(unittest.TestCase):
    """Unit tests for Host, Certificate, and Domain APIs."""

    def setUp(self):
        self.client = AsmClient()

    @patch("censys.common.base.requests.Session.get")
    def test_get_assets(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, ASSET_TYPE)
        assets = getattr(self.client, self.asset_type).get_assets()
        res = list(assets)

        assert RESOURCE_PAGING_RESULTS == res
        mock.assert_called_with(
            f"{ASSETS_URL}/{self.asset_type}",
            params={"pageNumber": 3, "pageSize": 500},
            timeout=TEST_TIMEOUT,
        )

    @patch("censys.common.base.requests.Session.get")
    def test_get_hosts_by_page(self, mock):
        mock.return_value = MockResponse(
            TEST_SUCCESS_CODE, ASSET_TYPE, TEST_PAGE_NUMBER
        )
        assets = getattr(self.client, self.asset_type).get_assets(
            page_number=TEST_PAGE_NUMBER, page_size=TEST_PAGE_SIZE
        )
        res = list(assets)

        assert RESOURCE_PAGING_RESULTS[:6] == res
        assert mock.call_args_list[0][1]["params"]["pageNumber"] != 1
        mock.assert_called_with(
            f"{ASSETS_URL}/{self.asset_type}",
            params={"pageNumber": 3, "pageSize": 2},
            timeout=TEST_TIMEOUT,
        )

    @patch("censys.common.base.requests.Session.get")
    def test_get_host_by_asset_id(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, ASSET_TYPE)
        getattr(self.client, self.asset_type).get_asset_by_id(self.test_asset_id)

        mock.assert_called_with(
            f"{ASSETS_URL}/{self.asset_type}/{self.test_asset_id}",
            params={},
            timeout=TEST_TIMEOUT,
        )

    @patch("censys.common.base.requests.Session.get")
    def test_get_host_comments(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, COMMENT_TYPE)
        comments = getattr(self.client, self.asset_type).get_comments(
            self.test_asset_id
        )
        res = list(comments)

        assert RESOURCE_PAGING_RESULTS == res
        mock.assert_called_with(
            f"{ASSETS_URL}/{self.asset_type}/{self.test_asset_id}/{COMMENT_TYPE}",
            params={"pageNumber": 3, "pageSize": 500},
            timeout=TEST_TIMEOUT,
        )

    @patch("censys.common.base.requests.Session.get")
    def test_get_host_comments_by_page(self, mock):
        mock.return_value = MockResponse(
            TEST_SUCCESS_CODE, COMMENT_TYPE, TEST_PAGE_NUMBER
        )
        comments = getattr(self.client, self.asset_type).get_comments(
            self.test_asset_id, page_number=2, page_size=2
        )
        res = list(comments)

        assert RESOURCE_PAGING_RESULTS[:6] == res
        assert mock.call_args_list[0][1]["params"]["pageNumber"] != 1
        mock.assert_called_with(
            f"{ASSETS_URL}/{self.asset_type}/{self.test_asset_id}/{COMMENT_TYPE}",
            params={"pageNumber": 3, "pageSize": 2},
            timeout=TEST_TIMEOUT,
        )

    @patch("censys.common.base.requests.Session.get")
    def test_get_comment_by_id(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, COMMENT_TYPE)
        getattr(self.client, self.asset_type).get_comment_by_id(
            self.test_asset_id, TEST_COMMENT_ID
        )

        mock.assert_called_with(
            (
                f"{ASSETS_URL}/{self.asset_type}/{self.test_asset_id}"
                f"/{COMMENT_TYPE}/{TEST_COMMENT_ID}"
            ),
            params={},
            timeout=TEST_TIMEOUT,
        )

    @patch("censys.common.base.requests.Session.post")
    def test_add_comment(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, COMMENT_TYPE)
        getattr(self.client, self.asset_type).add_comment(
            self.test_asset_id, TEST_COMMENT_TEXT
        )

        mock.assert_called_with(
            f"{ASSETS_URL}/{self.asset_type}/{self.test_asset_id}/{COMMENT_TYPE}",
            params={},
            timeout=TEST_TIMEOUT,
            json={"markdown": TEST_COMMENT_TEXT},
        )

    @patch("censys.common.base.requests.Session.delete")
    def test_delete_comment(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, ASSET_TYPE)
        getattr(self.client, self.asset_type).delete_comment(
            self.test_asset_id, TEST_COMMENT_ID
        )

        mock.assert_called_with(
            (
                f"{ASSETS_URL}/{self.asset_type}/{self.test_asset_id}"
                f"/comments/{TEST_COMMENT_ID}"
            ),
            params={},
            timeout=TEST_TIMEOUT,
        )

    @patch("censys.common.base.requests.Session.post")
    def test_add_tag_with_color(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, ASSET_TYPE)
        getattr(self.client, self.asset_type).add_tag(
            self.test_asset_id, TEST_TAG_NAME, TEST_TAG_COLOR
        )

        mock.assert_called_with(
            f"{ASSETS_URL}/{self.asset_type}/{self.test_asset_id}/tags",
            params={},
            timeout=TEST_TIMEOUT,
            json={"name": TEST_TAG_NAME, "color": TEST_TAG_COLOR},
        )

    def test_add_tag_with_invalid_color(self):
        with pytest.raises(CensysInvalidColorException):
            getattr(self.client, self.asset_type).add_tag(
                self.test_asset_id, TEST_TAG_NAME, TEST_INVALID_TAG_COLOR
            )

    @patch("censys.common.base.requests.Session.post")
    def test_add_tag_without_color(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, ASSET_TYPE)
        getattr(self.client, self.asset_type).add_tag(self.test_asset_id, TEST_TAG_NAME)

        mock.assert_called_with(
            f"{ASSETS_URL}/{self.asset_type}/{self.test_asset_id}/tags",
            params={},
            timeout=TEST_TIMEOUT,
            json={"name": TEST_TAG_NAME},
        )

    @patch("censys.common.base.requests.Session.delete")
    def test_delete_tag(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, ASSET_TYPE)
        getattr(self.client, self.asset_type).delete_tag(
            self.test_asset_id, TEST_TAG_NAME
        )

        mock.assert_called_with(
            (
                f"{ASSETS_URL}/{self.asset_type}/{self.test_asset_id}"
                f"/tags/{TEST_TAG_NAME}"
            ),
            params={},
            timeout=TEST_TIMEOUT,
        )

    @patch("censys.common.base.requests.Session.get")
    def test_get_subdomains(self, mock):
        if self.asset_type != "hosts":
            pytest.skip("Only applicable to hosts assets")
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, "subdomains")
        subdomains = self.client.domains.get_subdomains(self.test_asset_id)
        res = list(subdomains)

        assert RESOURCE_PAGING_RESULTS == res
        mock.assert_called_with(
            f"{ASSETS_URL}/domains/{self.test_asset_id}/subdomains",
            params={"pageNumber": 3, "pageSize": 500},
            timeout=TEST_TIMEOUT,
        )
