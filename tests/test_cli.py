import os
import csv
import json
import unittest
import contextlib
from io import StringIO
from unittest.mock import patch, mock_open

import pytest
import responses

from .utils import CensysTestCase

from censys.cli import main as cli_main
from censys.cli import CensysHNRI
from censys.exceptions import (
    CensysException,
    CensysCLIException,
)
from censys import __version__

BASE_URL = "https://censys.io/api/v1"
CLI_AUTH_ARGS = [
    "--api-id",
    CensysTestCase.api_id,
    "--api-secret",
    CensysTestCase.api_secret,
]
WROTE_PREFIX = "Wrote results to file"


def search_callback(request):
    payload = json.loads(request.body)
    resp_body = {
        "results": [{field: None for field in payload["fields"]}],
        "metadata": {"page": payload["page"], "pages": 100},
    }
    return (200, {}, json.dumps(resp_body))


class CensysCliTest(CensysTestCase):
    @patch("argparse._sys.argv", ["censys"])
    def test_default_help(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout), pytest.raises(SystemExit):
            cli_main()

        assert temp_stdout.getvalue().strip().startswith("usage: censys")

    @patch("argparse._sys.argv", ["censys", "--help"])
    def test_help(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout), pytest.raises(SystemExit):
            cli_main()

        stdout = temp_stdout.getvalue().strip()
        assert stdout.startswith("usage: censys")
        assert "search,hnri,config,config-asm" in stdout

    @patch("argparse._sys.argv", ["censys", "-v"])
    def test_version(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout), pytest.raises(SystemExit):
            cli_main()

        assert __version__ in temp_stdout.getvalue()


class CensysCliSearchTest(CensysTestCase):
    @patch("argparse._sys.argv", ["censys", "search", "--help"])
    def test_search_help(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout), pytest.raises(SystemExit):
            cli_main()

        assert temp_stdout.getvalue().strip().startswith("usage: censys search")

    @patch("argparse._sys.argv", ["censys", "search", "--query", "test"])
    @patch("builtins.open", new_callable=mock_open, read_data="[DEFAULT]")
    @patch.dict("os.environ", {"CENSYS_API_ID": "", "CENSYS_API_SECRET": ""})
    def test_no_creds(self, mock_file):
        with pytest.raises(
            CensysException, match="No API ID or API secret configured."
        ):
            cli_main()

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "search",
            "--query",
            "parsed.names: censys.io",
            "--index-type",
            "certs",
            "--fields",
            "parsed.issuer.country",
            "--format",
            "json",
            "--max-pages",
            "2",
        ]
        + CLI_AUTH_ARGS,
    )
    def test_write_json(self):
        self.responses.add_callback(
            responses.POST,
            BASE_URL + "/search/certificates",
            callback=search_callback,
            content_type="application/json",
        )

        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        cli_response = temp_stdout.getvalue().strip()
        assert cli_response.startswith(WROTE_PREFIX)

        json_path = cli_response.replace(WROTE_PREFIX, "").strip()
        assert json_path.endswith(".json")
        assert json_path.startswith("censys-query-output.")

        with open(json_path) as json_file:
            json_response = json.load(json_file)

        assert len(json_response) >= 1
        assert "parsed.issuer.country" in json_response[0]

        # Cleanup
        os.remove(json_path)

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "search",
            "--query",
            "8.8.8.8",
            "--index-type",
            "ipv4",
            "--fields",
            "protocols",
            "--format",
            "csv",
        ]
        + CLI_AUTH_ARGS,
    )
    def test_write_csv(self):
        self.responses.add_callback(
            responses.POST,
            BASE_URL + "/search/ipv4",
            callback=search_callback,
            content_type="application/json",
        )

        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        cli_response = temp_stdout.getvalue().strip()
        assert cli_response.startswith(WROTE_PREFIX)

        csv_path = cli_response.replace(WROTE_PREFIX, "").strip()
        assert csv_path.endswith(".csv")
        assert csv_path.startswith("censys-query-output.")

        with open(csv_path) as csv_file:
            csv_reader = csv.reader(csv_file)
            header = next(csv_reader)

        assert "protocols" in header

        # Cleanup
        os.remove(csv_path)

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "search",
            "--query",
            "parsed.names: censys.io",
            "--index-type",
            "certs",
            "--fields",
            "parsed.issuer.country",
            "--format",
            "json",
            "--output",
            "censys-certs.json",
        ]
        + CLI_AUTH_ARGS,
    )
    def test_write_output_path(self):
        self.responses.add_callback(
            responses.POST,
            BASE_URL + "/search/certificates",
            callback=search_callback,
            content_type="application/json",
        )

        output_path = "censys-certs.json"

        cli_main()

        assert os.path.isfile(output_path)

        with open(output_path) as json_file:
            json_response = json.load(json_file)

        assert len(json_response) >= 1
        assert "parsed.issuer.country" in json_response[0]

        # Cleanup
        os.remove(output_path)

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "search",
            "--query",
            "domain: censys.io AND ports: 443",
            "--index-type",
            "websites",
            "--fields",
            "443.https.get.headers.server",
            "--format",
            "screen",
        ]
        + CLI_AUTH_ARGS,
    )
    def test_write_screen(self):
        self.responses.add_callback(
            responses.POST,
            BASE_URL + "/search/websites",
            callback=search_callback,
            content_type="application/json",
        )

        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        json_response = json.loads(temp_stdout.getvalue().strip())

        assert len(json_response) >= 1
        assert "443.https.get.headers.server" in json_response[0]

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "search",
            "--query",
            "domain: censys.io AND ports: 443",
            "--index-type",
            "websites",
            "--overwrite",
            "--fields",
            "domain",
            "ports",
            "protocols",
            "443.https.tls.version",
            "443.https.tls.cipher_suite.name",
            "443.https.get.title",
            "443.https.get.headers.server",
            "--format",
            "screen",
        ]
        + CLI_AUTH_ARGS,
    )
    def test_overwrite(self):
        self.responses.add_callback(
            responses.POST,
            BASE_URL + "/search/websites",
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

        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        json_response = json.loads(temp_stdout.getvalue().strip())

        assert len(json_response) >= 1
        assert expected_fields == set(json_response[0].keys())

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "search",
            "--query",
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
        ]
        + CLI_AUTH_ARGS,
    )
    def test_field_max(self):
        with pytest.raises(
            CensysCLIException,
            match="Too many fields specified. The maximum number of fields is 20.",
        ):
            cli_main()


class CensysCliHNRITest(CensysTestCase):
    IPIFY_URL = "https://api.ipify.org?format=json"
    IP_ADDRESS = "8.8.8.8"

    def setUp(self):
        super().setUp()
        self.api = CensysHNRI(self.api_id, self.api_secret)
        self.base_url = self.api.index._api_url

    @patch(
        "argparse._sys.argv",
        ["censys", "hnri"] + CLI_AUTH_ARGS,
    )
    @patch("censys.cli.CensysHNRI.get_current_ip", return_value=IP_ADDRESS)
    def test_hnri_medium(self, mock_ip):
        self.responses.add(
            responses.GET,
            f"{self.base_url}/view/ipv4/{self.IP_ADDRESS}",
            status=200,
            json={"protocols": ["443/https", "53/dns", "21/banner"]},
        )

        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        stdout = temp_stdout.getvalue().strip()
        assert "Medium Risks Found:" in stdout
        assert "https on 443" in stdout
        assert "dns on 53" in stdout

    @patch(
        "argparse._sys.argv",
        ["censys", "hnri"] + CLI_AUTH_ARGS,
    )
    @patch("censys.cli.CensysHNRI.get_current_ip", return_value=IP_ADDRESS)
    def test_hnri_no_medium(self, mock_ip):
        self.responses.add(
            responses.GET,
            f"{self.base_url}/view/ipv4/{self.IP_ADDRESS}",
            status=200,
            json={"protocols": ["23/telnet"]},
        )

        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        stdout = temp_stdout.getvalue().strip()
        assert "High Risks Found:" in stdout
        assert "telnet on 23" in stdout
        assert "You don't have any Medium Risks in your network" in stdout

    @patch(
        "argparse._sys.argv",
        ["censys", "hnri"] + CLI_AUTH_ARGS,
    )
    @patch("censys.cli.CensysHNRI.get_current_ip", return_value=IP_ADDRESS)
    def test_hnri_not_found(self, mock_ip):
        self.responses.add(
            responses.GET,
            f"{self.base_url}/view/ipv4/{self.IP_ADDRESS}",
            status=404,
            json={
                "status": "error",
                "error_type": "unknown",
                "error": "We don't know anything about the specified host.",
            },
        )

        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        stdout = temp_stdout.getvalue().strip()
        assert "No Risks were found on your network" in stdout

    def test_get_current_ip(self):
        self.responses.add(
            responses.GET,
            self.IPIFY_URL,
            status=200,
            json={"ip": self.IP_ADDRESS},
        )
        ip_address = self.api.get_current_ip()
        assert ip_address == self.IP_ADDRESS

    def test_no_risks(self):
        with pytest.raises(CensysCLIException):
            self.api.risks_to_string([], [])


if __name__ == "__main__":
    unittest.main()
