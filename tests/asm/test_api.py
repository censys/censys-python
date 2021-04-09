import unittest
from unittest.mock import patch, mock_open

from requests.models import Response
from parameterized import parameterized

from ..utils import CensysTestCase

from censys.asm.api import CensysAsmAPI
from censys.exceptions import (
    CensysException,
    CensysAsmException,
    CensysExceptionMapper,
)


@patch.dict("os.environ", {"CENSYS_ASM_API_KEY": ""})
class CensysAPIBaseTestsNoAsmEnv(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data="[DEFAULT]")
    def test_no_env(self, mock_file):
        with self.assertRaises(CensysException) as context:
            CensysAsmAPI()

        self.assertIn("No ASM API key configured.", str(context.exception))


class CensysAsmAPITests(CensysTestCase):

    AsmExceptionParams = [
        (code, exception)
        for code, exception in CensysExceptionMapper.ASM_EXCEPTIONS.items()
    ]

    @parameterized.expand(AsmExceptionParams)
    @patch("requests.models.Response.json")
    def test_get_exception_class(self, status_code, exception, mock):
        response = Response()
        mock.return_value = {"errorCode": status_code}

        self.assertEqual(CensysAsmAPI()._get_exception_class(response), exception)

    def test_exception_repr(self):
        exception = CensysAsmException(
            404, "Unable to Find Seed", error_code=10014, details="[{id: 999}]"
        )

        self.assertEqual(
            repr(exception), "404 (Error Code: 10014), Unable to Find Seed. [{id: 999}]"
        )
