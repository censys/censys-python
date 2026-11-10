import argparse
from datetime import datetime

import pytest

from censys.cli.utils import valid_datetime_type, write_file
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

    def test_write_json_to_missing_directory(self, tmp_path):
        # Writing to a path in a directory that does not exist surfaces a
        # clean error (caught by the callers) instead of a raw traceback.
        with pytest.raises(ValueError, match="Could not write results"):
            write_file(
                {"key": "value"},
                file_format="json",
                file_path=str(tmp_path / "nope" / "out.json"),
            )
