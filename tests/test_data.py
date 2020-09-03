import unittest

from utils import CensysTestCase, primary_data_env

from censys.data import CensysData


class CensysDataTest(CensysTestCase):

    EXPECTED_GET_SERIES_KEYS = ["primary_series", "raw_series"]

    @classmethod
    def setUpClass(cls):
        cls._api = CensysData()

    def test_get_series(self):
        series = self._api.get_series()
        for key in self.EXPECTED_GET_SERIES_KEYS:
            self.assertTrue(key in series)

    @primary_data_env
    def test_view_series(self):
        series = "ipv4_2018"
        res = self._api.view_series(series)
        self.assertEqual(
            res["description"],
            "The Censys IPv4 dataset provides data about the services (e.g., HTTP, SMTP, MySQL) running on all publicly-accessible IPv4 hosts. This data series is produced by our newer data infrastructure and will replace the (deprecated) 'ipv4' series.",
        )
        self.assertIn("results", res)
        self.assertIn("historical", res["results"])
        self.assertIsInstance(res["results"]["historical"], list)

    @primary_data_env
    def test_view_result(self):
        series = "ipv4_2018"
        result = "20200818"
        res = self._api.view_result(series, result)

        self.assertEqual(res["id"], result)
        self.assertEqual(len(res["files"].keys()), 1035)
        self.assertEqual(res["total_size"], 347732264183)
        self.assertDictEqual(
            res["series"], {"id": "ipv4_2018", "name": "IPv4 Snapshots"}
        )


if __name__ == "__main__":
    unittest.main()
