import os
import csv
import json
import unittest
import contextlib
from io import StringIO
from unittest.mock import patch

from utils import required_env

from censys.cli import main as cli_main
from censys.exceptions import CensysException, CensysCLIException


class CensysCliTest(unittest.TestCase):
    @patch("argparse._sys.argv", ["censys", "--help"])
    def test_help(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            with self.assertRaises(SystemExit) as exit_event:
                cli_main()

        self.assertEqual(exit_event.exception.code, 0)
        self.assertTrue(temp_stdout.getvalue().strip().startswith("usage: censys"))

    @patch("argparse._sys.argv", ["censys", "test"])
    @patch.dict("os.environ", {"CENSYS_API_ID": "", "CENSYS_API_SECRET": ""})
    def test_no_creds(self):
        with self.assertRaises(CensysException) as exit_event:
            cli_main()

        self.assertEqual(
            str(exit_event.exception), "No API ID or API secret configured."
        )

    @required_env
    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "parsed.names: censys.io",
            "--query-type",
            "certs",
            "--fields",
            "parsed.issuer.country",
            "--output",
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
            "8.8.8.8",
            "--query-type",
            "ipv4",
            "--fields",
            "protocols",
            "--output",
            "csv",
            "--max-pages",
            "1",
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
            "censys.io",
            "--query-type",
            "websites",
            "--fields",
            "443.https.get.headers.server",
            "--output",
            "screen",
            "--max-pages",
            "1",
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
            "domain: censys.io AND ports: 443",
            "--query-type",
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
            "--output",
            "screen",
            "--max-pages",
            "1",
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
            "parsed.names: censys.io",
            "--query-type",
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


if __name__ == "__main__":
    unittest.main()
