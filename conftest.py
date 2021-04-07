import pytest
from unittest.mock import patch


@pytest.fixture(scope="module", autouse=True)
def mock_settings_env_vars():
    with patch.dict("os.environ", {"CENSYS_ASM_API_KEY": "testing"}):
        yield
