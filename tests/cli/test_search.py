import contextlib
import csv
import json
import os
from io import StringIO
from unittest.mock import mock_open, patch
from urllib.parse import urlencode

import pytest
import responses

from tests.search.v2.test_hosts import SEARCH_HOSTS_JSON
from tests.utils import V1_URL, V2_URL, CensysTestCase

from censys.cli import main as cli_main
from censys.common.exceptions import CensysCLIException, CensysException

WROTE_PREFIX = "Wrote results to file"


def search_callback(request):
    payload = json.loads(request.body)
    resp_body = {
        "results": [{field: None for field in payload["fields"]}],
        "metadata": {"page": payload["page"], "pages": 100},
    }
    return (200, {}, json.dumps(resp_body))


class CensysCliSearchTest(CensysTestCase):
    @patch("argparse._sys.argv", ["censys", "search", "--help"])
    def test_search_help(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout), pytest.raises(SystemExit):
            cli_main()

        assert temp_stdout.getvalue().strip().startswith("usage: censys search")

    @patch("argparse._sys.argv", ["censys", "search", "test"])
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
            "parsed.names: censys.io",
            "--index-type",
            "certs",
            "--fields",
            "parsed.issuer.country",
            "--format",
            "json",
        ]
        + CensysTestCase.cli_args,
    )
    def test_write_json(self):
        self.responses.add_callback(
            responses.POST,
            V1_URL + "/search/certificates",
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
        assert "censys-query-output." in json_path

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
            "parsed.names: censys.io",
            "--index-type",
            "certs",
            "--fields",
            "protocols",
            "--format",
            "csv",
        ]
        + CensysTestCase.cli_args,
    )
    def test_write_csv(self):
        self.responses.add_callback(
            responses.POST,
            V1_URL + "/search/certificates",
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
        assert "censys-query-output." in csv_path

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
        + CensysTestCase.cli_args,
    )
    def test_write_output_path(self):
        self.responses.add_callback(
            responses.POST,
            V1_URL + "/search/certificates",
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
            "domain: censys.io AND ports: 443",
            "--index-type",
            "certs",
            "--fields",
            "443.https.get.headers.server",
            "--format",
            "screen",
        ]
        + CensysTestCase.cli_args,
    )
    def test_write_screen(self):
        self.responses.add_callback(
            responses.POST,
            V1_URL + "/search/certificates",
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
            "--format",
            "screen",
        ]
        + CensysTestCase.cli_args,
    )
    def test_overwrite(self):
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
        + CensysTestCase.cli_args,
    )
    def test_field_max(self):
        with pytest.raises(
            CensysCLIException,
            match="Too many fields specified. The maximum number of fields is 20.",
        ):
            cli_main()

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "search",
            "parsed.names: censys.io",
            "--index-type",
            "certs",
            "--format",
            "screen",
            "--max-records",
            "2",
        ]
        + CensysTestCase.cli_args,
    )
    def test_max_records(self):
        self.responses.add_callback(
            responses.POST,
            V1_URL + "/search/certificates",
            callback=search_callback,
            content_type="application/json",
        )

        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        json_response = json.loads(temp_stdout.getvalue().strip())

        assert len(json_response) == 2

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "search",
            "service.service_name: HTTP",
            "--index-type",
            "hosts",
            "--format",
            "screen",
            "--pages",
            "1",
        ]
        + CensysTestCase.cli_args,
    )
    def test_write_screen_v2(self):
        self.responses.add(
            responses.GET,
            V2_URL
            + "/hosts/search?q=service.service_name: HTTP&per_page=100&virtual_hosts=EXCLUDE",
            status=200,
            json=SEARCH_HOSTS_JSON,
        )

        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        json_response = json.loads(temp_stdout.getvalue().strip())

        assert json_response == SEARCH_HOSTS_JSON["result"]["hits"]

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "search",
            "service.service_name: HTTP",
            "--index-type",
            "hosts",
            "--format",
            "screen",
            "--pages",
            "1",
            "--virtual-hosts",
            "ONLY",
        ]
        + CensysTestCase.cli_args,
    )
    def test_search_virtual_hosts(self):
        self.responses.add(
            responses.GET,
            V2_URL
            + "/hosts/search?q=service.service_name%3A+HTTP&per_page=100&virtual_hosts=ONLY",
            status=200,
            json=SEARCH_HOSTS_JSON,
        )

        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        json_response = json.loads(temp_stdout.getvalue().strip())

        assert json_response == SEARCH_HOSTS_JSON["result"]["hits"]

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "search",
            "service.service_name: HTTP",
            "--index-type",
            "hosts",
            "--format",
            "csv",
            "--pages",
            "1",
        ]
        + CensysTestCase.cli_args,
    )
    def test_write_csv_v2(self):
        with pytest.raises(
            CensysCLIException,
            match="CSV output is not supported for the hosts index.",
        ):
            cli_main()

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "search",
            "domain: censys.io AND ports: 443",
            "--index-type",
            "certs",
            "--open",
        ],
    )
    @patch("censys.cli.commands.search.webbrowser.open")
    def test_open_certificates(self, mock_open):
        with pytest.raises(SystemExit, match="0"):
            cli_main()
        query_str = urlencode({"q": "domain: censys.io AND ports: 443"})
        mock_open.assert_called_with(
            f"https://search.censys.io/certificates?{query_str}"
        )

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "search",
            "service.service_name: HTTP",
            "--index-type",
            "hosts",
            "--open",
        ],
    )
    @patch("censys.cli.commands.search.webbrowser.open")
    def test_open_v2(self, mock_open):
        with pytest.raises(SystemExit, match="0"):
            cli_main()
        query_str = urlencode({"q": "service.service_name: HTTP", "resource": "hosts"})
        mock_open.assert_called_with(f"https://search.censys.io/search?{query_str}")


if __name__ == "__main__":
    from unittest import main

    main()
