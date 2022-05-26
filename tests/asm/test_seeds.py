import unittest

import pytest
from pytest_mock import MockerFixture

from .utils import TEST_SUCCESS_CODE, TEST_TIMEOUT, V1_URL, MockResponse
from censys.asm.client import AsmClient

SEEDS_URL = f"{V1_URL}/seeds"
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

    def test_get_seeds(self):
        # Mock
        mock_request = self.mocker.patch("censys.common.base.requests.Session.get")
        mock_request.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        # Actual call
        self.client.seeds.get_seeds()
        # Assertions
        mock_request.assert_called_with(SEEDS_URL, params={}, timeout=TEST_TIMEOUT)

    def test_get_seeds_with_label(self):
        # Mock
        mock_request = self.mocker.patch("censys.common.base.requests.Session.get")
        mock_request.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        # Actual call
        self.client.seeds.get_seeds(seed_type="ASN", label=TEST_SEED_LABEL)
        # Assertions
        mock_request.assert_called_with(
            SEEDS_URL,
            params={"type": "ASN", "label": TEST_SEED_LABEL},
            timeout=TEST_TIMEOUT,
        )

    def test_get_seeds_by_type(self):
        # Mock
        mock_request = self.mocker.patch("censys.common.base.requests.Session.get")
        mock_request.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        # Actual call
        self.client.seeds.get_seeds(seed_type=TEST_SEED_TYPE)
        # Assertions
        mock_request.assert_called_with(
            SEEDS_URL, params={"type": TEST_SEED_TYPE}, timeout=TEST_TIMEOUT
        )

    def test_get_seed_by_id(self):
        # Mock
        mock_request = self.mocker.patch("censys.common.base.requests.Session.get")
        mock_request.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        # Actual call
        self.client.seeds.get_seed_by_id(TEST_SEED_ID)
        # Assertions
        mock_request.assert_called_with(
            f"{SEEDS_URL}/{TEST_SEED_ID}", params={}, timeout=TEST_TIMEOUT
        )

    def test_add_seed(self):
        # Mock
        mock_request = self.mocker.patch("censys.common.base.requests.Session.post")
        mock_request.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        # Actual call
        self.client.seeds.add_seeds([TEST_SEED])
        # Assertions
        mock_request.assert_called_with(
            SEEDS_URL,
            params={"force": None},
            timeout=TEST_TIMEOUT,
            json={"seeds": [TEST_SEED]},
        )

    def test_add_seeds(self):
        # Mock
        mock_request = self.mocker.patch("censys.common.base.requests.Session.post")
        mock_request.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        # Actual call
        self.client.seeds.add_seeds(TEST_SEED_LIST)
        # Assertions
        mock_request.assert_called_with(
            SEEDS_URL,
            params={"force": None},
            timeout=TEST_TIMEOUT,
            json={"seeds": TEST_SEED_LIST},
        )

    def test_add_seeds_forced(self):
        # Mock
        mock_request = self.mocker.patch("censys.common.base.requests.Session.post")
        mock_request.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        # Actual call
        self.client.seeds.add_seeds(TEST_SEED_LIST, force=True)
        # Assertions
        mock_request.assert_called_with(
            SEEDS_URL,
            params={"force": True},
            timeout=TEST_TIMEOUT,
            json={"seeds": TEST_SEED_LIST},
        )

    def test_replace_seeds_by_label(self):
        # Mock
        mock_request = self.mocker.patch("censys.common.base.requests.Session.put")
        mock_request.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        # Actual call
        self.client.seeds.replace_seeds_by_label(TEST_SEED_LABEL, [TEST_SEED_NO_LABEL])
        # Assertions
        mock_request.assert_called_with(
            SEEDS_URL,
            params={"label": "seed-test-label", "force": None},
            timeout=TEST_TIMEOUT,
            json={"seeds": [TEST_SEED_NO_LABEL]},
        )

    def test_replace_seeds_by_label_forced(self):
        # Mock
        mock_request = self.mocker.patch("censys.common.base.requests.Session.put")
        mock_request.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        # Actual call
        self.client.seeds.replace_seeds_by_label(
            TEST_SEED_LABEL, TEST_SEED_LIST_NO_LABEL, force=True
        )
        # Assertions
        mock_request.assert_called_with(
            SEEDS_URL,
            params={"label": "seed-test-label", "force": True},
            timeout=TEST_TIMEOUT,
            json={"seeds": TEST_SEED_LIST_NO_LABEL},
        )

    def test_delete_seeds_by_label(self):
        # Mock
        mock_request = self.mocker.patch("censys.common.base.requests.Session.delete")
        mock_request.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        # Actual call
        self.client.seeds.delete_seeds_by_label(TEST_SEED_LABEL)
        # Assertions
        mock_request.assert_called_with(
            SEEDS_URL, params={"label": TEST_SEED_LABEL}, timeout=TEST_TIMEOUT
        )

    def test_delete_seed_by_id(self):
        # Mock
        mock_request = self.mocker.patch("censys.common.base.requests.Session.delete")
        mock_request.return_value = MockResponse(TEST_SUCCESS_CODE, SEED_RESOURCE_TYPE)
        # Actual call
        self.client.seeds.delete_seed_by_id(TEST_SEED_ID)
        # Assertions
        mock_request.assert_called_with(
            f"{SEEDS_URL}/{TEST_SEED_ID}", params={}, timeout=TEST_TIMEOUT
        )
