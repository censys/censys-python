import json
import unittest
from unittest.mock import patch, mock_open

import pytest
import responses
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
        with pytest.raises(CensysException, match="No ASM API key configured."):
            CensysAsmAPI()


class CensysAsmAPITests(CensysTestCase):

    AsmExceptionParams = [
        (code, exception)
        for code, exception in CensysExceptionMapper.ASM_EXCEPTIONS.items()
    ]

    def setUp(self):
        super().setUp()
        self.setUpApi(CensysAsmAPI(self.api_id))

    @parameterized.expand(AsmExceptionParams)
    @patch("requests.models.Response.json")
    def test_get_exception_class(self, status_code, exception, mock):
        response = Response()
        mock.return_value = {"errorCode": status_code}

        assert CensysAsmAPI()._get_exception_class(response) == exception

    def test_exception_repr(self):
        exception = CensysAsmException(
            404, "Unable to Find Seed", error_code=10014, details="[{id: 999}]"
        )

        assert (
            repr(exception)
            == "404 (Error Code: 10014), Unable to Find Seed. [{id: 999}]"
        )

    @parameterized.expand([("assets"), ("comments"), ("tags"), ("subdomains")])
    def test_page_keywords(self, keyword):
        SECOND_PAGE = ["test4", "test5"]
        PAGE_JSON = {
            "pageNumber": 1,
            "totalPages": 2,
            keyword: ["test1", "test2", "test3"],
        }

        def keyword_callback(request):
            temp_json = PAGE_JSON.copy()
            pageNumber = int(request.params.get("pageNumber"))
            temp_json["pageNumber"] = pageNumber
            if pageNumber > 1:
                temp_json[keyword] = SECOND_PAGE
            return (200, {}, json.dumps(temp_json))

        self.responses.add_callback(
            responses.GET,
            f"{self.base_url}/{keyword}?pageNumber=",
            callback=keyword_callback,
        )

        res = list(self.api._get_page(f"/{keyword}"))

        assert res == PAGE_JSON[keyword] + SECOND_PAGE


if __name__ == "__main__":
    unittest.main()
