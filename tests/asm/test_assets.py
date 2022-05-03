import unittest
from unittest.mock import patch

import pytest
from parameterized import parameterized_class

from .utils import (
    RESOURCE_PAGING_RESULTS,
    TEST_SUCCESS_CODE,
    TEST_TIMEOUT,
    V1_URL,
    MockResponse,
)
from censys.asm.client import AsmClient
from censys.common.exceptions import CensysInvalidColorException

ASSETS_URL = f"{V1_URL}/assets"
ASSET_TYPE = "assets"
SUBDOMAIN_ASSET_TYPE = "subdomains"
COMMENT_TYPE = "comments"

TEST_PAGE_NUMBER = 2
TEST_PAGE_SIZE = 2

TEST_COMMENT_ID = 3
TEST_COMMENT_TEXT = "This is a test comment"
TEST_TAG_NAME = "asset-test-tag"
TEST_TAG_COLOR = "#4287f5"
TEST_INVALID_TAG_COLOR = "4287f5"


@parameterized_class(
    ("asset_type", "test_asset_id", "asset_type_config"),
    [
        ("hosts", "3.12.122.3"),
        (
            "certificates",
            "0006afc1ddc8431aa57c812adf028ab4f168b25bf5f06e94af86edbafa88dfe0",
        ),
        ("domains", "amazonaws.com"),
        ("subdomains", "s3.amazonaws.com", "amazonaws.com"),
    ],
)
class AssetsUnitTest(unittest.TestCase):
    """Unit tests for Host, Certificate, and Domain APIs."""

    def setUp(self):
        self.client = AsmClient()
        self.resource_type = (
            ASSET_TYPE if self.asset_type != "subdomains" else SUBDOMAIN_ASSET_TYPE
        )

    def get_asset_accessor(self):
        if self.asset_type == "subdomains":
            return self.client.get_subdomains(self.asset_type_config)
        return getattr(self.client, self.asset_type)

    def asset_type_url(self):
        if self.asset_type == "subdomains":
            return f"{ASSETS_URL}/domains/{self.asset_type_config}/{self.asset_type}"
        return f"{ASSETS_URL}/{self.asset_type}"

    def asset_id_url(self):
        return f"{self.asset_type_url()}/{self.test_asset_id}"

    @patch("censys.common.base.requests.Session.get")
    def test_get_assets(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, self.resource_type)
        assets = self.get_asset_accessor().get_assets()
        res = list(assets)

        assert RESOURCE_PAGING_RESULTS == res
        mock.assert_called_with(
            self.asset_type_url(),
            params={"pageNumber": 3, "pageSize": 500},
            timeout=TEST_TIMEOUT,
        )

    @patch("censys.common.base.requests.Session.get")
    def test_get_assets_by_tag(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, self.resource_type)
        assets = self.get_asset_accessor().get_assets(
            tag=[TEST_TAG_NAME], tag_operator="is", source=["Seed"], discovery_trail=True
        )
        res = list(assets)

        assert RESOURCE_PAGING_RESULTS == res
        mock.assert_called_with(
            self.asset_type_url(),
            params={
                "pageNumber": 3,
                "pageSize": 500,
                "tag": [TEST_TAG_NAME],
                "tagOperator": "is",
                "source": ["Seed"],
                "discoveryTrail": True,
            },
            timeout=TEST_TIMEOUT,
        )

    @patch("censys.common.base.requests.Session.get")
    def test_get_assets_by_page(self, mock):
        mock.return_value = MockResponse(
            TEST_SUCCESS_CODE, self.resource_type, TEST_PAGE_NUMBER
        )
        assets = self.get_asset_accessor().get_assets(
            page_number=TEST_PAGE_NUMBER, page_size=TEST_PAGE_SIZE
        )
        res = list(assets)

        assert RESOURCE_PAGING_RESULTS[:6] == res
        assert mock.call_args_list[0][1]["params"]["pageNumber"] != 1
        mock.assert_called_with(
            self.asset_type_url(),
            params={"pageNumber": 3, "pageSize": 2},
            timeout=TEST_TIMEOUT,
        )

    @patch("censys.common.base.requests.Session.get")
    def test_get_asset_by_asset_id(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, self.resource_type)
        self.get_asset_accessor().get_asset_by_id(self.test_asset_id)

        mock.assert_called_with(
            self.asset_id_url(),
            params={},
            timeout=TEST_TIMEOUT,
        )

    @patch("censys.common.base.requests.Session.get")
    def test_get_asset_comments(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, COMMENT_TYPE)
        comments = self.get_asset_accessor().get_comments(self.test_asset_id)
        res = list(comments)

        assert RESOURCE_PAGING_RESULTS == res
        mock.assert_called_with(
            f"{self.asset_id_url()}/{COMMENT_TYPE}",
            params={"pageNumber": 3, "pageSize": 500},
            timeout=TEST_TIMEOUT,
        )

    @patch("censys.common.base.requests.Session.get")
    def test_get_asset_comments_by_page(self, mock):
        mock.return_value = MockResponse(
            TEST_SUCCESS_CODE, COMMENT_TYPE, TEST_PAGE_NUMBER
        )
        comments = self.get_asset_accessor().get_comments(
            self.test_asset_id, page_number=2, page_size=2
        )
        res = list(comments)

        assert RESOURCE_PAGING_RESULTS[:6] == res
        assert mock.call_args_list[0][1]["params"]["pageNumber"] != 1
        mock.assert_called_with(
            f"{self.asset_id_url()}/{COMMENT_TYPE}",
            params={"pageNumber": 3, "pageSize": 2},
            timeout=TEST_TIMEOUT,
        )

    @patch("censys.common.base.requests.Session.get")
    def test_get_comment_by_id(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, COMMENT_TYPE)
        self.get_asset_accessor().get_comment_by_id(self.test_asset_id, TEST_COMMENT_ID)

        mock.assert_called_with(
            (f"{self.asset_id_url()}/{COMMENT_TYPE}/{TEST_COMMENT_ID}"),
            params={},
            timeout=TEST_TIMEOUT,
        )

    @patch("censys.common.base.requests.Session.post")
    def test_add_comment(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, COMMENT_TYPE)
        self.get_asset_accessor().add_comment(self.test_asset_id, TEST_COMMENT_TEXT)

        mock.assert_called_with(
            f"{self.asset_id_url()}/{COMMENT_TYPE}",
            params={},
            timeout=TEST_TIMEOUT,
            json={"markdown": TEST_COMMENT_TEXT},
        )

    @patch("censys.common.base.requests.Session.delete")
    def test_delete_comment(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, self.resource_type)
        self.get_asset_accessor().delete_comment(self.test_asset_id, TEST_COMMENT_ID)

        mock.assert_called_with(
            (f"{self.asset_id_url()}/comments/{TEST_COMMENT_ID}"),
            params={},
            timeout=TEST_TIMEOUT,
        )

    @patch("censys.common.base.requests.Session.post")
    def test_add_tag_with_color(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, self.resource_type)
        self.get_asset_accessor().add_tag(
            self.test_asset_id, TEST_TAG_NAME, TEST_TAG_COLOR
        )

        mock.assert_called_with(
            f"{self.asset_id_url()}/tags",
            params={},
            timeout=TEST_TIMEOUT,
            json={"name": TEST_TAG_NAME, "color": TEST_TAG_COLOR},
        )

    def test_add_tag_with_invalid_color(self):
        with pytest.raises(CensysInvalidColorException):
            self.get_asset_accessor().add_tag(
                self.test_asset_id, TEST_TAG_NAME, TEST_INVALID_TAG_COLOR
            )

    @patch("censys.common.base.requests.Session.post")
    def test_add_tag_without_color(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, self.resource_type)
        self.get_asset_accessor().add_tag(self.test_asset_id, TEST_TAG_NAME)

        mock.assert_called_with(
            f"{self.asset_id_url()}/tags",
            params={},
            timeout=TEST_TIMEOUT,
            json={"name": TEST_TAG_NAME},
        )

    @patch("censys.common.base.requests.Session.delete")
    def test_delete_tag(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, self.resource_type)
        self.get_asset_accessor().delete_tag(self.test_asset_id, TEST_TAG_NAME)

        mock.assert_called_with(
            (f"{self.asset_id_url()}/tags/{TEST_TAG_NAME}"),
            params={},
            timeout=TEST_TIMEOUT,
        )

    @patch("censys.common.base.requests.Session.get")
    def test_get_subdomains(self, mock):
        if self.asset_type != "domains":
            pytest.skip("Only applicable to domains assets")
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, "subdomains")
        subdomains = self.client.domains.get_subdomains(self.test_asset_id)
        res = list(subdomains)

        assert RESOURCE_PAGING_RESULTS == res
        mock.assert_called_with(
            f"{self.asset_id_url()}/subdomains",
            params={"pageNumber": 3, "pageSize": 500},
            timeout=TEST_TIMEOUT,
        )
