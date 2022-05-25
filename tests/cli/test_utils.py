import argparse
from datetime import datetime

import pytest
from parameterized import parameterized

from tests.utils import CensysTestCase

from censys.cli.utils import valid_datetime_type


class CensysCliUtilsTest(CensysTestCase):
    @parameterized.expand(
        [
            ["2021-05-20", datetime(2021, 5, 20)],
            ["2021-05-20 12:00", datetime(2021, 5, 20, 12, 00)],
        ]
    )
    def test_valid_datetime(self, string, expected):
        # Actual call
        actual = valid_datetime_type(string)
        # Assertions
        assert actual == expected

    @parameterized.expand(
        [
            ["2021/05/20"],
            ["2021/05/20 12:00"],
        ]
    )
    def test_invalid_datetime(self, string):
        # Actuall call/error raising
        with pytest.raises(argparse.ArgumentTypeError):
            valid_datetime_type(string)
