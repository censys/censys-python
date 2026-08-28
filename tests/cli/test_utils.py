import argparse
from datetime import datetime

import pytest

from censys.cli.utils import valid_datetime_type
from tests.utils import CensysTestCase


class CensysCliUtilsTest(CensysTestCase):
    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("2021-05-20", datetime(2021, 5, 20)),
            ("2021-05-20 12:00", datetime(2021, 5, 20, 12, 00)),
        ],
    )
    def test_valid_datetime(self, string, expected):
        # Actual call
        actual = valid_datetime_type(string)
        # Assertions
        assert actual == expected

    @pytest.mark.parametrize(
        "string",
        [
            "2021/05/20",
            "2021/05/20 12:00",
        ],
    )
    def test_invalid_datetime(self, string):
        # Actuall call/error raising
        with pytest.raises(argparse.ArgumentTypeError):
            valid_datetime_type(string)
