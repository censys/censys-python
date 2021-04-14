import json
import unittest
from unittest.mock import patch

from censys.asm.client import AsmClient
from .utils import (
    MockResponse,
    TEST_SUCCESS_CODE,
    TEST_TIMEOUT,
    BASE_URL,
)

SEEDS_URL = f"{BASE_URL}/seeds"
SEED_RESOURCE_TYPE = "seeds"

TEST_SEED_ID = 6
TEST_SEED_LABEL = "seed-test-label"
TEST_SEED_TYPE = "DOMAIN_NAME"

TEST_SEED = {"type": "ASN", "value": 90000, "label": "seed-test-label"}
TEST_SEED_NO_LABEL = {
    "type": "ASN",
    "value": 90001,
}
TEST_SEED_LIST = [
    {"type": "ASN", "value": 90002, "label": "seed-test-label"},
    {"type": "ASN", "value": 90003, "label": "seed-test-label"},
    {"type": "ASN", "value": 90004, "label": "seed-test-label"},
]
TEST_SEED_LIST_NO_LABEL = [
    {"type": "ASN", "value": 90002},
    {"type": "ASN", "value": 90003},
    {"type": "ASN", "value": 90004},
]


class SeedsUnitTests(unittest.TestCase):
    """Unit tests for Seeds API."""

    def setUp(self):
        self.client = AsmClient()

    @patch("censys.base.requests.Session.get")
    def test_get_seeds(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        self.client.seeds.get_seeds()

        mock.assert_called_with(SEEDS_URL, params={"type": None}, timeout=TEST_TIMEOUT)

    @patch("censys.base.requests.Session.get")
    def test_get_seeds_by_type(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        self.client.seeds.get_seeds(seed_type=TEST_SEED_TYPE)

        mock.assert_called_with(
            SEEDS_URL, params={"type": TEST_SEED_TYPE}, timeout=TEST_TIMEOUT
        )

    @patch("censys.base.requests.Session.get")
    def test_get_seed_by_id(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        self.client.seeds.get_seed_by_id(TEST_SEED_ID)

        mock.assert_called_with(
            f"{SEEDS_URL}/{TEST_SEED_ID}", params={}, timeout=TEST_TIMEOUT
        )

    @patch("censys.base.requests.Session.post")
    def test_add_seed(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        self.client.seeds.add_seeds([TEST_SEED])

        mock.assert_called_with(
            SEEDS_URL,
            params={"force": False},
            timeout=TEST_TIMEOUT,
            data=json.dumps({"seeds": [TEST_SEED]}),
        )

    @patch("censys.base.requests.Session.post")
    def test_add_seeds(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        self.client.seeds.add_seeds(TEST_SEED_LIST)

        mock.assert_called_with(
            SEEDS_URL,
            params={"force": False},
            timeout=TEST_TIMEOUT,
            data=json.dumps({"seeds": TEST_SEED_LIST}),
        )

    @patch("censys.base.requests.Session.post")
    def test_add_seeds_forced(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        self.client.seeds.add_seeds(TEST_SEED_LIST, force=True)

        mock.assert_called_with(
            SEEDS_URL,
            params={"force": True},
            timeout=TEST_TIMEOUT,
            data=json.dumps({"seeds": TEST_SEED_LIST}),
        )

    @patch("censys.base.requests.Session.put")
    def test_replace_seeds_by_label(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        self.client.seeds.replace_seeds_by_label(TEST_SEED_LABEL, [TEST_SEED_NO_LABEL])

        mock.assert_called_with(
            SEEDS_URL,
            params={"label": "seed-test-label", "force": False},
            timeout=TEST_TIMEOUT,
            data=json.dumps({"seeds": [TEST_SEED_NO_LABEL]}),
        )

    @patch("censys.base.requests.Session.put")
    def test_replace_seeds_by_label_forced(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        self.client.seeds.replace_seeds_by_label(
            TEST_SEED_LABEL, TEST_SEED_LIST_NO_LABEL, force=True
        )

        mock.assert_called_with(
            SEEDS_URL,
            params={"label": "seed-test-label", "force": True},
            timeout=TEST_TIMEOUT,
            data=json.dumps({"seeds": TEST_SEED_LIST_NO_LABEL}),
        )

    @patch("censys.base.requests.Session.delete")
    def test_delete_seeds_by_label(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        self.client.seeds.delete_seeds_by_label(TEST_SEED_LABEL)

        mock.assert_called_with(
            SEEDS_URL, params={"label": TEST_SEED_LABEL}, timeout=TEST_TIMEOUT
        )

    @patch("censys.base.requests.Session.delete")
    def test_delete_seed_by_id(self, mock):
        mock.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        self.client.seeds.delete_seed_by_id(TEST_SEED_ID)

        mock.assert_called_with(
            f"{SEEDS_URL}/{TEST_SEED_ID}", params={}, timeout=TEST_TIMEOUT
        )


if __name__ == "__main__":
    unittest.main()
