import contextlib
import csv
import json
import os
from io import StringIO
from typing import Dict, Tuple
from unittest.mock import mock_open
from urllib.parse import urlencode

import pytest
import responses
from requests import PreparedRequest

from tests.search.v2.test_hosts import SEARCH_HOSTS_JSON, TOO_MANY_REQUESTS_ERROR_JSON
from tests.utils import V1_URL, V2_URL, CensysTestCase

from censys.cli import main as cli_main
from censys.common.exceptions import CensysCLIException, CensysException

WROTE_PREFIX = "Wrote results to file"


def search_callback(request: PreparedRequest) -> Tuple[int, Dict[str, str], str]:
    payload = json.loads(request.body)
    resp_body = {
        "results": [{field: None for field in payload["fields"]}],
        "metadata": {"page": payload["page"], "pages": 100},
    }
    return (200, {}, json.dumps(resp_body))


def search_callback_fail(request: PreparedRequest) -> Tuple[int, Dict[str, str], str]:
    payload = json.loads(request.body)
    if payload.get("page", 1) >= 2:
        return (
            429,
            {},
            json.dumps({"error_code": 429, "error": "rate limit exceeded"}),
        )
    return search_callback(request)


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
            "builtins.open", new_callable=mock_open, read_data="[DEFAULT]"
        )
        self.mocker.patch.dict(
            "os.environ", {"CENSYS_API_ID": "", "CENSYS_API_SECRET": ""}
        )
        # Actual Call/Assertion
        with pytest.raises(
            CensysException, match="No API ID or API secret configured."
        ):
            cli_main()

    def test_write_json(self):
        # Set up Response
        self.responses.add_callback(
            responses.POST,
            V1_URL + "/search/certificates",
            callback=search_callback,
            content_type="application/json",
        )
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "parsed.names: censys.io",
                "--index-type",
                "certs",
                "--fields",
                "parsed.issuer.country",
                "--output",
                "censys-certs.json",
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
        assert "censys-certs." in json_path

        with open(json_path) as json_file:
            json_response = json.load(json_file)

        assert len(json_response) >= 1
        assert "parsed.issuer.country" in json_response[0]

        # Cleanup
        os.remove(json_path)

    def test_write_csv(self):
        # Set up response
        self.responses.add_callback(
            responses.POST,
            V1_URL + "/search/certificates",
            callback=search_callback,
            content_type="application/json",
        )
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "parsed.names: censys.io",
                "--index-type",
                "certs",
                "--fields",
                "protocols",
                "--output",
                "censys-certs.csv",
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

        csv_path = cli_response.replace(WROTE_PREFIX, "").strip()
        assert csv_path.endswith(".csv")
        assert "censys-certs." in csv_path

        with open(csv_path) as csv_file:
            csv_reader = csv.reader(csv_file)
            header = next(csv_reader)

        assert "protocols" in header

        # Cleanup
        os.remove(csv_path)

    def test_write_invalid_output_path(self):
        # Setup response
        self.responses.add_callback(
            responses.POST,
            V1_URL + "/search/certificates",
            callback=search_callback,
            content_type="application/json",
        )
        # mock
        self.patch_args(
            [
                "censys",
                "search",
                "parsed.names: censys.io",
                "--index-type",
                "certs",
                "--fields",
                "parsed.issuer.country",
                "--output",
                "censys-certs.html",
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
        assert json_path.endswith(".html")
        assert "censys-certs." in json_path

        with open(json_path) as json_file:
            json_response = json.load(json_file)

        assert len(json_response) >= 1
        assert "parsed.issuer.country" in json_response[0]

        # Cleanup
        os.remove(json_path)

    def test_write_screen(self):
        # Set up response
        self.responses.add_callback(
            responses.POST,
            V1_URL + "/search/certificates",
            callback=search_callback,
            content_type="application/json",
        )
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "domain: censys.io AND ports: 443",
                "--index-type",
                "certs",
                "--fields",
                "443.https.get.headers.server",
            ],
            search_auth=True,
        )

        temp_stdout = StringIO()
        # Actual call
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        json_response = json.loads(temp_stdout.getvalue().strip())
        # Assertions
        assert len(json_response) >= 1
        assert "443.https.get.headers.server" in json_response[0]

    def test_overwrite(self):
        # Setup response
        self.responses.add_callback(
            responses.POST,
            V1_URL + "/search/certificates",
            callback=search_callback,
            content_type="application/json",
        )

        expected_fields = {
            "domain",
            "ports",
            "protocols",
            "443.https.tls.version",
            "443.https.tls.cipher_suite.name",
            "443.https.get.title",
            "443.https.get.headers.server",
        }
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "parsed.names: censys.io",
                "--index-type",
                "certs",
                "--overwrite",
                "--fields",
                "domain",
                "ports",
                "protocols",
                "443.https.tls.version",
                "443.https.tls.cipher_suite.name",
                "443.https.get.title",
                "443.https.get.headers.server",
            ],
            search_auth=True,
        )

        temp_stdout = StringIO()
        # Actual call
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        json_response = json.loads(temp_stdout.getvalue().strip())
        # Assertions
        assert len(json_response) >= 1
        assert expected_fields == set(json_response[0].keys())

    def test_field_max(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "parsed.names: censys.io",
                "--index-type",
                "certs",
                "--fields",
                "fingerprint_sha256",
                "parent_spki_subject_fingerprint",
                "parents",
                "metadata.added_at",
                "metadata.parse_error",
                "metadata.parse_status",
                "metadata.parse_version",
                "metadata.post_processed",
                "parsed.fingerprint_md5",
                "parsed.fingerprint_sha1",
                "parsed.fingerprint_sha256",
                "parsed.issuer_dn",
                "parsed.names",
                "parsed.redacted",
                "parsed.serial_number",
                "parsed.spki_subject_fingerprint",
                "parsed.subject_dn",
                "parsed.tbs_fingerprint",
                "parsed.tbs_noct_fingerprint",
                "parsed.validation_level",
                "parsed.version",
            ],
            search_auth=True,
        )
        # Actual call/error raising
        with pytest.raises(
            CensysCLIException,
            match="Too many fields specified. The maximum number of fields is 20.",
        ):
            cli_main()

    def test_max_records(self):
        # Setup response
        self.responses.add_callback(
            responses.POST,
            V1_URL + "/search/certificates",
            callback=search_callback,
            content_type="application/json",
        )
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "parsed.names: censys.io",
                "--index-type",
                "certs",
                "--max-records",
                "2",
            ],
            search_auth=True,
        )

        temp_stdout = StringIO()
        # Actual call
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        json_response = json.loads(temp_stdout.getvalue().strip())
        # Assertions
        assert len(json_response) == 2

    def test_midway_fail(self):
        # Setup response
        self.responses.add_callback(
            responses.POST,
            V1_URL + "/search/certificates",
            callback=search_callback_fail,
            content_type="application/json",
        )
        # Mock
        self.patch_args(
            ["censys", "search", "parsed.names: censys.io", "--index-type", "certs"],
            search_auth=True,
        )

        temp_stdout = StringIO()
        # Actual call
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        json_response = json.loads(temp_stdout.getvalue().strip())
        # Assertions
        assert len(json_response) == 1

    def test_write_screen_v2(self):
        # Setup response
        self.responses.add(
            responses.GET,
            V2_URL
            + "/hosts/search?q=service.service_name: HTTP&per_page=100&sort=RELEVANCE&virtual_hosts=EXCLUDE",
            status=200,
            json=SEARCH_HOSTS_JSON,
        )
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "service.service_name: HTTP",
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
            responses.GET,
            V2_URL
            + "/hosts/search?q=service.service_name%3A+HTTP&per_page=100&sort=RELEVANCE&virtual_hosts=ONLY",
            status=200,
            json=SEARCH_HOSTS_JSON,
        )
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "service.service_name: HTTP",
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
            responses.GET,
            V2_URL
            + "/hosts/search?q=service.service_name%3A+HTTP&per_page=100&sort=RANDOM&virtual_hosts=EXCLUDE",
            status=200,
            json=SEARCH_HOSTS_JSON,
        )
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "service.service_name: HTTP",
                "--index-type",
                "hosts",
                "--pages",
                "1",
                "--sort-order",
                "RANDOM",
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

    def test_write_json_v2(self):
        # Setup response
        self.responses.add(
            responses.GET,
            V2_URL
            + "/hosts/search?q=service.service_name: HTTP&per_page=100&sort=RELEVANCE&virtual_hosts=EXCLUDE",
            status=200,
            json=SEARCH_HOSTS_JSON,
        )
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "service.service_name: HTTP",
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

    def test_write_csv_v2(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "service.service_name: HTTP",
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

    def test_midway_fail_v2(self):
        # Setup response
        next_cursor = SEARCH_HOSTS_JSON["result"]["links"]["next"]
        self.responses.add(
            responses.GET,
            V2_URL
            + "/hosts/search?q=service.service_name: HTTP&per_page=100&sort=RELEVANCE&virtual_hosts=EXCLUDE",
            status=200,
            json=SEARCH_HOSTS_JSON,
        )
        self.responses.add(
            responses.GET,
            V2_URL
            + f"/hosts/search?q=service.service_name: HTTP&per_page=100&sort=RELEVANCE&virtual_hosts=EXCLUDE&cursor={next_cursor}",
            status=429,
            json=TOO_MANY_REQUESTS_ERROR_JSON,
        )
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "service.service_name: HTTP",
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
                "certs",
                "--open",
            ],
        )
        mock_open = self.mocker.patch("censys.cli.commands.search.webbrowser.open")

        # Actual call/error raising
        with pytest.raises(SystemExit, match="0"):
            cli_main()
        query_str = urlencode({"q": "domain: censys.io AND ports: 443"})
        # Assertions
        mock_open.assert_called_with(
            f"https://search.censys.io/certificates?{query_str}"
        )

    def test_open_v2(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "search",
                "service.service_name: HTTP",
                "--index-type",
                "hosts",
                "--open",
            ],
        )
        mock_open = self.mocker.patch("censys.cli.commands.search.webbrowser.open")
        # Actual call/error raising
        with pytest.raises(SystemExit, match="0"):
            cli_main()
        query_str = urlencode({"q": "service.service_name: HTTP", "resource": "hosts"})
        # Assertions
        mock_open.assert_called_with(f"https://search.censys.io/search?{query_str}")


if __name__ == "__main__":
    from unittest import main

    main()
