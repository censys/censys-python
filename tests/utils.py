import os

import pytest


REQUIRED_ENV = ["CENSYS_API_ID", "CENSYS_API_SECRET"]
required_env = pytest.mark.skipif(
    not all([os.getenv(env_var) for env_var in REQUIRED_ENV]),
    reason=f"missing required environment variables: {REQUIRED_ENV}",
)
