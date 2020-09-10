import os
import unittest

import pytest

from censys.config import DEFAULT, get_config

config = get_config()
api_id = config.get(DEFAULT, "api_id") or os.getenv("CENSYS_API_ID")
api_secret = config.get(DEFAULT, "api_secret") or os.getenv("CENSYS_API_SECRET")


required_env = pytest.mark.skipif(
    not (api_id and api_secret), reason="API credentials not found",
)

permissions_env = pytest.mark.skipif(
    not os.getenv("PERMISSIONS"), reason="(optional) enterprise permissions required",
)


@required_env
class CensysTestCase(unittest.TestCase):
    pass
