import json
import unittest

import pytest
import responses
from parameterized import parameterized
from pytest_mock import MockerFixture
from requests.models import Response

from ..utils import CensysTestCase
from censys.asm.api import CensysAsmAPI
from censys.common.exceptions import (
    CensysAsmException,
    CensysException,
    CensysExceptionMapper,
)


class CensysAPIBaseTestsNoAsmEnv(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker: MockerFixture):
        """Injects fixtures into the test case.

        Args:
            mocker (MockerFixture): pytest-mock fixture.
        """
        # Inject mocker fixture
        self.mocker = mocker

    def setUp(self):
        self.responses = responses.RequestsMock()
        self.responses.start()
        self.mocker.patch.dict("os.environ", {"CENSYS_ASM_API_KEY": ""})
        self.mock_open = self.mocker.patch(
            "builtins.open", new_callable=self.mocker.mock_open, read_data="[DEFAULT]"
        )

        self.addCleanup(self.responses.stop)
        self.addCleanup(self.responses.reset)

    def test_no_env(self):
        self.mocker.patch(
            "builtins.open", new_callable=self.mock_open, read_data="[DEFAULT]"
        )
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
    def test_get_exception_class(self, status_code, exception):
        # Mock
        mock_response = self.mocker.patch("requests.models.Response.json")

        response = Response()
        mock_response.return_value = {"errorCode": status_code}
        # Actual call/assertion
        assert CensysAsmAPI()._get_exception_class(response) == exception

    def test_exception_repr(self):
        # Actual call
        exception = CensysAsmException(
            404,
            "Unable to Find Seed",
            error_code=10014,
            details="[{id: 999}]",  # noqa: FS003
        )
        # Assertion
        assert (
            repr(exception)
            == "404 (Error Code: 10014), Unable to Find Seed. [{id: 999}]"  # noqa: FS003
        )

    @parameterized.expand([("assets")])
    def test_page_keywords(self, keyword):
        # Mock
        page_json = {
            "pageNumber": 1,
            "totalPages": 2,
            keyword: ["test1", "test2", "test3"],
        }
        second_page = ["test4", "test5"]

        def keyword_callback(request):
            temp_json = page_json.copy()
            page_number = int(request.params.get("pageNumber"))
            temp_json["pageNumber"] = page_number
            if page_number > 1:
                temp_json[keyword] = second_page
            return (200, {}, json.dumps(temp_json))

        # Actual call
        self.responses.add_callback(
            responses.GET,
            f"{self.base_url}/{keyword}?pageNumber=",
            callback=keyword_callback,
        )

        res = list(self.api._get_page(f"/{keyword}"))
        # Assertions
        assert res == page_json[keyword] + second_page

    def test_get_workspace_id(self):
        self.responses.add(
            responses.GET,
            f"{self.base_url}/integrations/v1/account",
            status=200,
            json={"workspaceId": "test-workspace-id"},
        )

        # Actual call
        res = self.api.get_workspace_id()

        # Assertions
        assert res == "test-workspace-id"
