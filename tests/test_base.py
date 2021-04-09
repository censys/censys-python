from unittest.mock import patch

from requests.models import Response

from .utils import CensysTestCase

from censys.base import CensysAPIBase
from censys.exceptions import (
    CensysException,
    CensysAPIException,
)


class CensysAPIBaseTests(CensysTestCase):
    def test_base_get_exception_class(self):
        base = CensysAPIBase("url")

        self.assertEqual(base._get_exception_class(Response()), CensysAPIException)

    @patch.dict("os.environ", {"CENSYS_API_URL": ""})
    def test_no_api_url(self):
        with self.assertRaises(CensysException) as context:
            CensysAPIBase()

        self.assertIn("No API url configured.", str(context.exception))

    @patch("censys.base.requests.Session.get")
    def test_successful_empty_json_response(self, mock):
        mock_response = Response()
        mock_response.status_code = 200
        mock.return_value = mock_response
        base = CensysAPIBase("url")

        self.assertEqual({}, base._make_call(base._session.get, "endpoint"))