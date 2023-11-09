import argparse
import contextlib
import json
import os
from io import StringIO
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode

import pytest
import responses
from parameterized import parameterized
from requests import PreparedRequest
from responses import matchers

from tests.search.v2.test_certs import SEARCH_CERTS_JSON
from tests.search.v2.test_hosts import (
    SEARCH_HOSTS_JSON,
    SERVER_ERROR_JSON,
    TOO_MANY_REQUESTS_ERROR_JSON,
)
from tests.utils import V2_URL, CensysTestCase

from censys.cli import main as cli_main
from censys.cli.commands.search import (
    CERTIFICATES_AUTOCOMPLETE,
    HOSTS_AUTOCOMPLETE,
    fields_completer,
)
from censys.common.exceptions import CensysCLIException, CensysException

WROTE_PREFIX = "Wrote results to file"


def search_callback(request: PreparedRequest) -> Tuple[int, Dict[str, str], str]:
    payload = json.loads(request.body)  # type: ignore
    resp_body = {
        "result": {
            "query": payload["q"],
            "hits": [{"parsed.names": ["censys.io"], "parsed.issuer.country": "US"}],
        },
        "links": {
            "prev": None,
            "next": "test-next-cursor",
        },
    }
    return (200, {}, json.dumps(resp_body))


class CensysCliSearchTest(CensysTestCase):
    def test_search_help(self):
        # Mock
        self.patch_args(["censys", "search", "--help"])

        # Actual call
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout), pytest.raises(SystemExit):
            cli_main()

        # Assertions
        assert temp_stdout.getvalue().strip().startswith("usage: censys search")

    def test_no_creds(self):
        # Mock
        self.patch_args(["censys", "search", "test"])
        self.mocker.patch(
            "builtins.open", new_callable=self.mocker.mock_open, read_data="[DEFAULT]"
        )
        self.mocker.patch.dict(
            "os.environ", {"CENSYS_API_ID": "", "CENSYS_API_SECRET": ""}
        )
        # Actual Call/Assertion
        with pytest.raises(
            CensysException, match="No API ID or API secret configured."
        ):
            cli_main()

    def test_invalid_timeout(self):
        # mock
        self.patch_args(
            [
                "censys",
                "search",
                "parsed.names: censys.io",
                "--index-type",
                "certificates",
                "--timeout",
                "-1",
            ],
            search_auth=True,
        )

        # Actual call
        with pytest.raises(
            CensysCLIException,
            match="Timeout must be greater than 0.",
        ):
            cli_main()

    def test_write_invalid_output_path(self):
        # Setup response
        self.responses.add(
            responses.POST,
            V2_URL + "/certificates/search",
            json=SEARCH_CERTS_JSON,
        )
        # mock
        self.patch_args(
            [
                "censys",
                "search",
                "parsed.names: censys.io",
                "--index-type",
                "certificates",
                "--fields",
                "parsed.issuer.country",
                "--output",
                "censys-certs.html",
            ],
            search_auth=True,
        )

        # Actual call
        with pytest.raises(
            CensysCLIException,
            match="JSON is the only valid file format for Search 2.0 responses.",
        ):
            cli_main()

    def test_write_screen(self):
        # Setup response
        self.responses.add(
            responses.POST,
            V2_URL + "/hosts/search",
            status=200,
            json=SEARCH_HOSTS_JSON,
            match=[
                matchers.json_params_matcher(
                    {
                        "q": "services.service_name: HTTP",
                        "per_page": 100,
                        "sort": "RELEVANCE",
                        "virtual_hosts": "EXCLUDE",
                    }
                )
            ],
        )
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "services.service_name: HTTP",
                "--index-type",
                "hosts",
                "--pages",
                "1",
            ],
            search_auth=True,
        )

        temp_stdout = StringIO()
        # Actual call
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        json_response = json.loads(temp_stdout.getvalue().strip())
        # Assertions
        assert json_response == SEARCH_HOSTS_JSON["result"]["hits"]

    def test_search_virtual_hosts(self):
        # Setup response
        self.responses.add(
            responses.POST,
            V2_URL + "/hosts/search",
            status=200,
            json=SEARCH_HOSTS_JSON,
            match=[
                matchers.json_params_matcher(
                    {
                        "q": "services.service_name: HTTP",
                        "per_page": 100,
                        "sort": "RELEVANCE",
                        "virtual_hosts": "ONLY",
                    }
                )
            ],
        )
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "services.service_name: HTTP",
                "--index-type",
                "hosts",
                "--pages",
                "1",
                "--virtual-hosts",
                "ONLY",
            ],
            search_auth=True,
        )

        temp_stdout = StringIO()
        # Actual call
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        json_response = json.loads(temp_stdout.getvalue().strip())
        # Assertions
        assert json_response == SEARCH_HOSTS_JSON["result"]["hits"]

    def test_search_sort_order(self):
        # Setup response
        self.responses.add(
            responses.POST,
            V2_URL + "/hosts/search",
            status=200,
            json=SEARCH_HOSTS_JSON,
            match=[
                matchers.json_params_matcher(
                    {
                        "q": "services.service_name: HTTP",
                        "per_page": 100,
                        "sort": "DESCENDING",
                        "virtual_hosts": "EXCLUDE",
                    }
                )
            ],
        )
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "services.service_name: HTTP",
                "--index-type",
                "hosts",
                "--pages",
                "1",
                "--sort-order",
                "DESCENDING",
            ],
            search_auth=True,
        )

        temp_stdout = StringIO()
        # Actual call
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        json_response = json.loads(temp_stdout.getvalue().strip())
        # Assertions
        assert json_response == SEARCH_HOSTS_JSON["result"]["hits"]

    def test_write_json(self):
        # Setup response
        self.responses.add(
            responses.POST,
            V2_URL + "/hosts/search",
            status=200,
            json=SEARCH_HOSTS_JSON,
            match=[
                matchers.json_params_matcher(
                    {
                        "q": "services.service_name: HTTP",
                        "per_page": 100,
                        "sort": "RELEVANCE",
                        "virtual_hosts": "EXCLUDE",
                    }
                )
            ],
        )
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "services.service_name: HTTP",
                "--index-type",
                "hosts",
                "--pages",
                "1",
                "--output",
                "censys-hosts.json",
            ],
            search_auth=True,
        )

        temp_stdout = StringIO()
        # Actual call
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        cli_response = temp_stdout.getvalue().strip()
        # Assertions
        assert cli_response.startswith(WROTE_PREFIX)

        json_path = cli_response.replace(WROTE_PREFIX, "").strip()
        assert json_path.endswith(".json")
        assert "censys-hosts." in json_path

        with open(json_path) as json_file:
            json_response = json.load(json_file)

        assert len(json_response) >= 1
        assert json_response == SEARCH_HOSTS_JSON["result"]["hits"]

        # Cleanup
        os.remove(json_path)

    def test_write_csv_fail(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "services.service_name: HTTP",
                "--index-type",
                "hosts",
                "--pages",
                "1",
                "--output",
                "censys-hosts.csv",
            ],
            search_auth=True,
        )
        # Actual call/error raising
        with pytest.raises(
            CensysCLIException,
            match="JSON is the only valid file format for Search 2.0 responses.",
        ):
            cli_main()

    @parameterized.expand(
        [
            (429, TOO_MANY_REQUESTS_ERROR_JSON),
            (500, SERVER_ERROR_JSON),
        ]
    )
    def test_midway_fail(self, status_code: int, json_response: dict):
        # Setup response
        next_cursor = SEARCH_HOSTS_JSON["result"]["links"]["next"]
        self.responses.add(
            responses.POST,
            V2_URL + "/hosts/search",
            status=200,
            json=SEARCH_HOSTS_JSON,
            match=[
                matchers.json_params_matcher(
                    {
                        "q": "services.service_name: HTTP",
                        "per_page": 100,
                        "sort": "RELEVANCE",
                        "virtual_hosts": "EXCLUDE",
                    }
                )
            ],
        )
        self.responses.add(
            responses.POST,
            V2_URL + "/hosts/search",
            status=status_code,
            json=json_response,
            match=[
                matchers.json_params_matcher(
                    {
                        "q": "services.service_name: HTTP",
                        "per_page": 100,
                        "sort": "RELEVANCE",
                        "virtual_hosts": "EXCLUDE",
                        "cursor": next_cursor,
                    }
                )
            ],
        )
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "services.service_name: HTTP",
                "--index-type",
                "hosts",
                "--pages",
                "2",
                "--output",
                "censys-hosts.json",
            ],
            search_auth=True,
        )

        temp_stdout = StringIO()
        # Actual call
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        cli_response = temp_stdout.getvalue().strip()
        # Assertions
        assert cli_response.startswith(WROTE_PREFIX)

        json_path = cli_response.replace(WROTE_PREFIX, "").strip()
        assert json_path.endswith(".json")
        assert "censys-hosts." in json_path

        with open(json_path) as json_file:
            json_response = json.load(json_file)

        assert len(json_response) >= 1
        assert json_response == SEARCH_HOSTS_JSON["result"]["hits"]

        # Cleanup
        os.remove(json_path)

    def test_open_certificates(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "domain: censys.io AND ports: 443",
                "--index-type",
                "certificates",
                "--open",
            ],
        )
        mock_open = self.mocker.patch("censys.cli.commands.search.webbrowser.open")

        # Actual call/error raising
        with pytest.raises(SystemExit, match="0"):
            cli_main()
        query_str = urlencode(
            {"q": "domain: censys.io AND ports: 443", "resource": "certificates"}
        )
        # Assertions
        mock_open.assert_called_with(f"https://search.censys.io/search?{query_str}")

    def test_open_hosts(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "services.service_name: HTTP",
                "--index-type",
                "hosts",
                "--open",
            ],
        )
        mock_open = self.mocker.patch("censys.cli.commands.search.webbrowser.open")
        # Actual call/error raising
        with pytest.raises(SystemExit, match="0"):
            cli_main()
        query_str = urlencode({"q": "services.service_name: HTTP", "resource": "hosts"})
        # Assertions
        mock_open.assert_called_with(f"https://search.censys.io/search?{query_str}")

    @parameterized.expand(
        [
            ("hosts", HOSTS_AUTOCOMPLETE),
            ("hosts", HOSTS_AUTOCOMPLETE, "service"),
            ("certificates", CERTIFICATES_AUTOCOMPLETE),
            ("invalid"),
        ]
    )
    def test_fields_completer(
        self,
        index_type: str,
        autocomplete_file: Optional[Path] = None,
        prefix: str = "",
    ):
        parsed_args = argparse.Namespace(index_type=index_type)
        if autocomplete_file is None:
            expected_fields = []
        else:
            expected_fields = json.load(autocomplete_file.open())["data"]
            expected_fields = [
                field_value
                for field in expected_fields
                if not (field_value := field["value"]).endswith(".type")
            ]
            if prefix == "":
                expected_fields = expected_fields[:20]
        assert (
            fields_completer(prefix=prefix, parsed_args=parsed_args) == expected_fields
        )


if __name__ == "__main__":
    from unittest import main

    main()
