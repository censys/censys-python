import os
import csv
import json
import unittest
import contextlib
from io import StringIO
from unittest.mock import patch, mock_open

from tests.utils import required_env

from censys.cli import main as cli_main
from censys.cli import CensysHNRI
from censys.exceptions import (
    CensysException,
    CensysCLIException,
    CensysNotFoundException,
)
from censys.config import config_path


class CensysCliSearchTest(unittest.TestCase):
    @patch("argparse._sys.argv", ["censys"])
    def test_default_help(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            with self.assertRaises(SystemExit) as exit_event:
                cli_main()

        self.assertEqual(exit_event.exception.code, 0)
        self.assertTrue(temp_stdout.getvalue().strip().startswith("usage: censys"))

    @patch("argparse._sys.argv", ["censys", "--help"])
    def test_help(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            with self.assertRaises(SystemExit) as exit_event:
                cli_main()

        self.assertEqual(exit_event.exception.code, 0)
        stdout = temp_stdout.getvalue().strip()
        self.assertTrue(stdout.startswith("usage: censys"))
        self.assertIn("search,hnri,config", stdout)

    @patch("argparse._sys.argv", ["censys", "search", "--help"])
    def test_search_help(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            with self.assertRaises(SystemExit) as exit_event:
                cli_main()

        self.assertEqual(exit_event.exception.code, 0)
        self.assertTrue(
            temp_stdout.getvalue().strip().startswith("usage: censys search")
        )

    @patch("argparse._sys.argv", ["censys", "search", "--query", "test"])
    @patch("builtins.open", new_callable=mock_open, read_data="[DEFAULT]")
    @patch.dict("os.environ", {"CENSYS_API_ID": "", "CENSYS_API_SECRET": ""})
    def test_no_creds(self, mock_file):
        with self.assertRaises(CensysException) as exit_event:
            cli_main()

        mock_file.assert_called_with(config_path, "w")

        self.assertEqual(
            str(exit_event.exception), "No API ID or API secret configured."
        )

    @required_env
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
        ],
    )
    def test_write_json(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        PREFIX = "Wrote results to file"

        cli_response = temp_stdout.getvalue().strip()
        self.assertTrue(cli_response.startswith(PREFIX))

        json_path = cli_response.replace(PREFIX, "").strip()
        self.assertTrue(json_path.endswith(".json"))
        self.assertTrue(json_path.startswith("censys-query-output."))
        self.assertTrue(os.path.isfile(json_path))

        with open(json_path) as json_file:
            json_response = json.load(json_file)

        self.assertGreaterEqual(len(json_response), 1)
        self.assertIn("parsed.issuer.country", json_response[0].keys())

        # Cleanup
        os.remove(json_path)

    @required_env
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
        ],
    )
    def test_write_csv(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        PREFIX = "Wrote results to file"

        cli_response = temp_stdout.getvalue().strip()
        self.assertTrue(cli_response.startswith(PREFIX))

        csv_path = cli_response.replace(PREFIX, "").strip()
        self.assertTrue(csv_path.endswith(".csv"))
        self.assertTrue(csv_path.startswith("censys-query-output."))
        self.assertTrue(os.path.isfile(csv_path))

        with open(csv_path) as csv_file:
            csv_reader = csv.reader(csv_file)
            header = next(csv_reader)

        self.assertIn("protocols", header)

        # Cleanup
        os.remove(csv_path)

    @required_env
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
        ],
    )
    def test_write_output_path(self):
        output_path = "censys-certs.json"

        cli_main()

        self.assertTrue(os.path.isfile(output_path))

        with open(output_path) as json_file:
            json_response = json.load(json_file)

        self.assertGreaterEqual(len(json_response), 1)
        self.assertIn("parsed.issuer.country", json_response[0].keys())

        # Cleanup
        os.remove(output_path)

    @required_env
    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "search",
            "--query",
            "censys.io",
            "--index-type",
            "websites",
            "--fields",
            "443.https.get.headers.server",
            "--format",
            "screen",
        ],
    )
    def test_write_screen(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        json_response = json.loads(temp_stdout.getvalue().strip())

        self.assertGreaterEqual(len(json_response), 1)
        self.assertIn("443.https.get.headers.server", json_response[0].keys())

    @required_env
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
        ],
    )
    def test_overwrite(self):
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

        self.assertGreaterEqual(len(json_response), 1)
        self.assertSetEqual(expected_fields, set(json_response[0].keys()))

    @required_env
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
        ],
    )
    def test_field_max(self):
        with self.assertRaises(CensysCLIException) as exit_event:
            cli_main()

        self.assertEqual(
            str(exit_event.exception),
            "Too many fields specified. The maximum number of fields is 20.",
        )


class CensysCliHNRITest(unittest.TestCase):
    @required_env
    @patch(
        "argparse._sys.argv",
        ["censys", "hnri"],
    )
    @patch("censys.cli.CensysHNRI.get_current_ip", lambda _: "8.8.8.8")
    @patch(
        "censys.ipv4.CensysIPv4.view",
        lambda _, ip: {"protocols": ["443/https", "53/dns", "21/banner"]},
    )
    def test_hnri_medium(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        stdout = temp_stdout.getvalue().strip()
        self.assertIn("Medium Risks Found:", stdout)
        self.assertIn("https on 443", stdout)
        self.assertIn("dns on 53", stdout)

    @required_env
    @patch(
        "argparse._sys.argv",
        ["censys", "hnri"],
    )
    @patch("censys.cli.CensysHNRI.get_current_ip", lambda _: "94.142.241.111")
    @patch("censys.ipv4.CensysIPv4.view", lambda _, ip: {"protocols": ["23/telnet"]})
    def test_hnri_high(self):
        # Using towel.blinkenlights.nl/94.142.241.111
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        stdout = temp_stdout.getvalue().strip()
        self.assertIn("High Risks Found:", stdout)
        self.assertIn("telnet on 23", stdout)

    @required_env
    @patch(
        "argparse._sys.argv",
        ["censys", "hnri"],
    )
    @patch("censys.ipv4.CensysIPv4.view", lambda _, ip: {"protocols": ["23/telnet"]})
    def test_hnri_no_medium(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        stdout = temp_stdout.getvalue().strip()
        self.assertIn("High Risks Found:", stdout)
        self.assertIn("telnet on 23", stdout)
        self.assertIn("You don't have any Medium Risks in your network", stdout)

    @required_env
    @patch(
        "argparse._sys.argv",
        ["censys", "hnri"],
    )
    @patch("censys.cli.CensysHNRI.get_current_ip", lambda _: "8.8.8.8")
    @patch(
        "censys.ipv4.CensysIPv4.view",
        side_effect=CensysNotFoundException(
            404, "The requested record does not exist."
        ),
    )
    def test_hnri_not_found(self, view):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        view.assert_called_with("8.8.8.8")

        stdout = temp_stdout.getvalue().strip()
        self.assertIn("No Risks were found on your network", stdout)

    def test_get_current_ip(self):
        ip_address = CensysHNRI.get_current_ip()
        self.assertIsInstance(ip_address, str)

    def test_no_risks(self):
        with self.assertRaises(CensysCLIException):
            CensysHNRI.risks_to_string([], [])


if __name__ == "__main__":
    unittest.main()
