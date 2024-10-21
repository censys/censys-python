"""Pytest Shared Fixtures.

For more details see: https://docs.pytest.org/en/stable/fixture.html
"""

from unittest.mock import patch

import pytest


@pytest.fixture(scope="module", autouse=True)
def _mock_settings_env_vars():
    with patch.dict("os.environ", {"CENSYS_ASM_API_KEY": "testing"}):
        yield
