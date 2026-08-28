import datetime

import pytest

from censys.common.utils import format_iso8601, format_rfc3339


class UtilsTest:
    @pytest.mark.parametrize(
        ("since", "actual"),
        [
            ("2021-01-01", "2021-01-01"),
            (datetime.date(2021, 1, 1), "2021-01-01T00:00:00.000000Z"),
            (
                datetime.datetime(2021, 1, 1, 12, 15, 20, 40),
                "2021-01-01T12:15:20.000040Z",
            ),
        ],
    )
    def test_format_rfc3339(self, since, actual):
        assert format_rfc3339(since) == actual

    @pytest.mark.parametrize(
        ("since", "actual"),
        [
            ("2021-01-01", "2021-01-01"),
            (datetime.date(2021, 1, 1), "2021-01-01"),
            (datetime.datetime(2021, 1, 1, 12, 15, 20, 40), "2021-01-01"),
        ],
    )
    def test_format_iso8601(self, since, actual):
        assert format_iso8601(since) == actual
