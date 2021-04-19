import json
import unittest
from unittest.mock import patch

from parameterized import parameterized

from .utils import (
    BASE_URL,
    RESOURCE_PAGING_RESULTS,
    TEST_SUCCESS_CODE,
    TEST_TIMEOUT,
    MockResponse,
)

from censys.asm.client import AsmClient

ASSETS_URL = f"{BASE_URL}/assets"
ASSET_TYPE = "assets"
COMMENT_TYPE = "comments"

TEST_PAGE_NUMBER = 2
TEST_PAGE_SIZE = 2
TEST_ASSET_IDS = {
    "hosts": "3.12.122.3",
    "certificates": "0006afc1ddc8431aa57c812adf028ab4f168b25bf5f06e94af86edbafa88dfe0",
    "domains": "amazonaws.com",
}

TEST_COMMENT_ID = 3
TEST_COMMENT_TEXT = "This is a test comment"
TEST_TAG_NAME = "asset-test-tag"
TEST_TAG_COLOR = "#4287f5"


class AssetsUnitTest(unittest.TestCase):
    """Unit tests for Host, Certificate, and Domain APIs."""

    def setUp(self):
        self.client = AsmClient()

    @parameterized.expand([["hosts"], ["certificates"], ["domains"]])
    @patch("censys.base.requests.Session.get")
    def test_get_assets(self, asset_type, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, ASSET_TYPE)
        assets = getattr(self.client, asset_type).get_assets()
        res = list(assets)

        assert RESOURCE_PAGING_RESULTS == res
        mock.assert_called_with(
            f"{ASSETS_URL}/{asset_type}",
            params={"pageNumber": 3, "pageSize": 500},
            timeout=TEST_TIMEOUT,
        )

    @parameterized.expand([["hosts"], ["certificates"], ["domains"]])
    @patch("censys.base.requests.Session.get")
    def test_get_hosts_by_page(self, asset_type, mock):
        mock.return_value = MockResponse(
            TEST_SUCCESS_CODE, ASSET_TYPE, TEST_PAGE_NUMBER
        )
        assets = getattr(self.client, asset_type).get_assets(
            page_number=TEST_PAGE_NUMBER, page_size=TEST_PAGE_SIZE
        )
        res = list(assets)

        assert RESOURCE_PAGING_RESULTS[:6] == res
        assert mock.call_args_list[0][1]["params"]["pageNumber"] != 1
        mock.assert_called_with(
            f"{ASSETS_URL}/{asset_type}",
            params={"pageNumber": 3, "pageSize": 2},
            timeout=TEST_TIMEOUT,
        )

    @parameterized.expand([["hosts"], ["certificates"], ["domains"]])
    @patch("censys.base.requests.Session.get")
    def test_get_host_by_asset_id(self, asset_type, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, ASSET_TYPE)
        getattr(self.client, asset_type).get_asset_by_id(TEST_ASSET_IDS[asset_type])

        mock.assert_called_with(
            f"{ASSETS_URL}/{asset_type}/{TEST_ASSET_IDS[asset_type]}",
            params={},
            timeout=TEST_TIMEOUT,
        )

    @parameterized.expand([["hosts"], ["certificates"], ["domains"]])
    @patch("censys.base.requests.Session.get")
    def test_get_host_comments(self, asset_type, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, COMMENT_TYPE)
        comments = getattr(self.client, asset_type).get_comments(
            TEST_ASSET_IDS[asset_type]
        )
        res = list(comments)

        assert RESOURCE_PAGING_RESULTS == res
        mock.assert_called_with(
            f"{ASSETS_URL}/{asset_type}/{TEST_ASSET_IDS[asset_type]}/{COMMENT_TYPE}",
            params={"pageNumber": 3, "pageSize": 500},
            timeout=TEST_TIMEOUT,
        )

    @parameterized.expand([["hosts"], ["certificates"], ["domains"]])
    @patch("censys.base.requests.Session.get")
    def test_get_host_comments_by_page(self, asset_type, mock):
        mock.return_value = MockResponse(
            TEST_SUCCESS_CODE, COMMENT_TYPE, TEST_PAGE_NUMBER
        )
        comments = getattr(self.client, asset_type).get_comments(
            TEST_ASSET_IDS[asset_type], page_number=2, page_size=2
        )
        res = list(comments)

        assert RESOURCE_PAGING_RESULTS[:6] == res
        assert mock.call_args_list[0][1]["params"]["pageNumber"] != 1
        mock.assert_called_with(
            f"{ASSETS_URL}/{asset_type}/{TEST_ASSET_IDS[asset_type]}/{COMMENT_TYPE}",
            params={"pageNumber": 3, "pageSize": 2},
            timeout=TEST_TIMEOUT,
        )

    @parameterized.expand([["hosts"], ["certificates"], ["domains"]])
    @patch("censys.base.requests.Session.get")
    def test_get_comment_by_id(self, asset_type, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, COMMENT_TYPE)
        getattr(self.client, asset_type).get_comment_by_id(
            TEST_ASSET_IDS[asset_type], TEST_COMMENT_ID
        )

        mock.assert_called_with(
            (
                f"{ASSETS_URL}/{asset_type}/{TEST_ASSET_IDS[asset_type]}"
                f"/{COMMENT_TYPE}/{TEST_COMMENT_ID}"
            ),
            params={},
            timeout=TEST_TIMEOUT,
        )

    @parameterized.expand([["hosts"], ["certificates"], ["domains"]])
    @patch("censys.base.requests.Session.post")
    def test_add_host_comment(self, asset_type, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, COMMENT_TYPE)
        getattr(self.client, asset_type).add_comment(
            TEST_ASSET_IDS[asset_type], TEST_COMMENT_TEXT
        )

        mock.assert_called_with(
            f"{ASSETS_URL}/{asset_type}/{TEST_ASSET_IDS[asset_type]}/{COMMENT_TYPE}",
            params={},
            timeout=TEST_TIMEOUT,
            data=json.dumps({"markdown": TEST_COMMENT_TEXT}),
        )

    @parameterized.expand([["hosts"], ["certificates"], ["domains"]])
    @patch("censys.base.requests.Session.post")
    def test_add_host_tag_with_color(self, asset_type, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, ASSET_TYPE)
        getattr(self.client, asset_type).add_tag(
            TEST_ASSET_IDS[asset_type], TEST_TAG_NAME, TEST_TAG_COLOR
        )

        mock.assert_called_with(
            f"{ASSETS_URL}/{asset_type}/{TEST_ASSET_IDS[asset_type]}/tags",
            params={},
            timeout=TEST_TIMEOUT,
            data=json.dumps({"name": TEST_TAG_NAME, "color": TEST_TAG_COLOR}),
        )

    @parameterized.expand([["hosts"], ["certificates"], ["domains"]])
    @patch("censys.base.requests.Session.post")
    def test_add_host_tag_without_color(self, asset_type, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, ASSET_TYPE)
        getattr(self.client, asset_type).add_tag(
            TEST_ASSET_IDS[asset_type], TEST_TAG_NAME
        )

        mock.assert_called_with(
            f"{ASSETS_URL}/{asset_type}/{TEST_ASSET_IDS[asset_type]}/tags",
            params={},
            timeout=TEST_TIMEOUT,
            data=json.dumps({"name": TEST_TAG_NAME}),
        )

    @parameterized.expand([["hosts"], ["certificates"], ["domains"]])
    @patch("censys.base.requests.Session.delete")
    def test_delete_host_tag(self, asset_type, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, ASSET_TYPE)
        getattr(self.client, asset_type).delete_tag(
            TEST_ASSET_IDS[asset_type], TEST_TAG_NAME
        )

        mock.assert_called_with(
            (
                f"{ASSETS_URL}/{asset_type}/{TEST_ASSET_IDS[asset_type]}"
                f"/tags/{TEST_TAG_NAME}"
            ),
            params={},
            timeout=TEST_TIMEOUT,
        )

    @patch("censys.base.requests.Session.get")
    def test_get_subdomains(self, mock):
        test_domain = TEST_ASSET_IDS.get("domains")
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, "subdomains")
        subdomains = self.client.domains.get_subdomains(test_domain)
        res = list(subdomains)

        assert RESOURCE_PAGING_RESULTS == res
        mock.assert_called_with(
            f"{ASSETS_URL}/domains/{test_domain}/subdomains",
            params={"pageNumber": 3, "pageSize": 500},
            timeout=TEST_TIMEOUT,
        )


if __name__ == "__main__":
    unittest.main()
