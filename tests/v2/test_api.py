import unittest
from unittest.mock import patch, mock_open

import pytest
from requests.models import Response
from parameterized import parameterized

from ..utils import CensysTestCase

from censys.v2.api import CensysSearchAPIv2
from censys.exceptions import (
    CensysException,
    CensysExceptionMapper,
)

SearchExceptionParams = [
    (code, exception)
    for code, exception in CensysExceptionMapper.SEARCH_EXCEPTIONS.items()
]


class CensysSearchAPITests(CensysTestCase):
    def setUp(self):
        super().setUp()
        self.setUpApi(CensysSearchAPIv2(self.api_id, self.api_secret))

    @parameterized.expand(SearchExceptionParams)
    def test_get_exception_class(self, status_code, exception):
        response = Response()
        response.status_code = status_code

        assert self.api._get_exception_class(response) == exception


@patch.dict("os.environ", {"CENSYS_API_ID": "", "CENSYS_API_SECRET": ""})
class CensysAPIBaseTestsNoSearchEnv(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data="[DEFAULT]")
    def test_no_env(self, mock_file):
        with pytest.raises(
            CensysException, match="No API ID or API secret configured."
        ):
            CensysSearchAPIv2()


if __name__ == "__main__":
    unittest.main()
