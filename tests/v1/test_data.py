import unittest

from ..utils import CensysTestCase, permissions_env

from censys.v1.data import CensysData


class CensysDataTest(CensysTestCase):

    EXPECTED_GET_SERIES_KEYS = ["primary_series", "raw_series"]

    @classmethod
    def setUpClass(cls):
        cls._api = CensysData()

    def test_get_series(self):
        series = self._api.get_series()
        for key in self.EXPECTED_GET_SERIES_KEYS:
            assert key in series

    @permissions_env
    def test_view_series(self):
        series = "ipv4_2018"
        res = self._api.view_series(series)

        assert "description" in res
        assert "results" in res
        assert "historical" in res["results"]
        assert isinstance(res["results"]["historical"], list)

    @permissions_env
    def test_view_result(self):
        series = "ipv4_2018"
        result = "20200818"
        res = self._api.view_result(series, result)

        assert res["id"] == result
        assert len(res["files"].keys()) == 1035
        assert res["total_size"] == 347732264183
        assert res["series"] == {"id": series, "name": "IPv4 Snapshots"}


if __name__ == "__main__":
    unittest.main()
