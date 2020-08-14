import unittest

from utils import required_env

from censys.base import CensysAPIBase


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


if __name__ == "__main__":
    unittest.main()
