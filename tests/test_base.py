import unittest
from unittest.mock import patch

from utils import required_env

from censys.base import (
    CensysAPIBase,
    CensysException,
    CensysUnauthorizedException,
    CensysNotFoundException,
    CensysRateLimitExceededException,
)


@required_env
class CensysAPIBaseTests(unittest.TestCase):

    EXPECTED_MY_ACCOUNT_KEYS = {"email", "first_login", "last_login", "login", "quota"}
    EXPECTED_QUOTA_KEYS = {"allowance", "resets_at", "used"}

    @classmethod
    def setUpClass(cls):
        cls._api = CensysAPIBase()

    # as mentioned here https://censysio.atlassian.net/browse/DATA-586
    # this endpoint no longer returns api id / secret
    def test_my_account(self):
        res = self._api.account()
        self.assertSetEqual(set(res.keys()), self.EXPECTED_MY_ACCOUNT_KEYS)
        self.assertSetEqual(set(res["quota"].keys()), self.EXPECTED_QUOTA_KEYS)

    def test_get_exception_class(self):
        self.assertEqual(
            self._api._get_exception_class(403), CensysUnauthorizedException
        )
        self.assertEqual(self._api._get_exception_class(404), CensysNotFoundException)
        self.assertEqual(
            self._api._get_exception_class(429), CensysRateLimitExceededException
        )

    def test_exception_repr(self):
        exception = CensysException(404, "Not Found", const="notfound")
        self.assertEqual(repr(exception), "404 (notfound): Not Found")


@patch.dict("os.environ", {"CENSYS_API_ID": "", "CENSYS_API_SECRET": ""})
class CensysAPIBaseTestsNoEnv(unittest.TestCase):
    def test_no_env(self):
        with self.assertRaises(CensysException) as context:
            CensysAPIBase()

        self.assertIn("No API ID or API secret configured.", str(context.exception))


if __name__ == "__main__":
    unittest.main()
