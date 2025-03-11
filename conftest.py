"""Pytest Shared Fixtures.

For more details see: https://docs.pytest.org/en/stable/fixture.html
"""

from unittest.mock import patch

import pytest


@pytest.fixture(scope="module", autouse=True)
def _mock_settings_env_vars():
    with patch.dict("os.environ", {"CENSYS_ASM_API_KEY": "testing"}):
        yield


def pytest_addoption(parser):
    """Add command-line options to pytest.

    Args:
        parser: The pytest command-line parser
    """
    parser.addoption(
        "--run-e2e",
        action="store_true",
        default=False,
        help="Run end-to-end tests that make real API calls",
    )
