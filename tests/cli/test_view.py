import contextlib
import json
import os
from io import StringIO
from unittest.mock import mock_open, patch

import pytest
import responses

from tests.cli.test_search import WROTE_PREFIX
from tests.search.v2.test_hosts import VIEW_HOST_JSON
from tests.utils import V2_URL, CensysTestCase

from censys.cli import main as cli_main
from censys.common.exceptions import CensysException


class CensysCliSearchTest(CensysTestCase):
    @patch("argparse._sys.argv", ["censys", "view", "--help"])
    def test_search_help(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout), pytest.raises(SystemExit):
            cli_main()

        assert temp_stdout.getvalue().strip().startswith("usage: censys view")

    @patch("argparse._sys.argv", ["censys", "view", "test"])
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
            "view",
            "8.8.8.8",
            "--index-type",
            "hosts",
            "--format",
            "json",
        ]
        + CensysTestCase.cli_args,
    )
    def test_write_json(self):
        self.responses.add(
            responses.GET,
            V2_URL + "/hosts/8.8.8.8",
            status=200,
            json=VIEW_HOST_JSON,
        )

        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        cli_response = temp_stdout.getvalue().strip()
        assert cli_response.startswith(WROTE_PREFIX)

        json_path = cli_response.replace(WROTE_PREFIX, "").strip()
        assert json_path.endswith(".json")
        assert "censys-view-8.8.8.8." in json_path

        with open(json_path) as json_file:
            json_response = json.load(json_file)

        assert VIEW_HOST_JSON["result"] == json_response

        # Cleanup
        os.remove(json_path)

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "view",
            "8.8.8.8",
            "--format",
            "json",
            "--output",
            "censys-google-dns.json",
        ]
        + CensysTestCase.cli_args,
    )
    def test_write_output_path(self):
        self.responses.add(
            responses.GET,
            V2_URL + "/hosts/8.8.8.8",
            status=200,
            json=VIEW_HOST_JSON,
        )

        output_path = "censys-google-dns.json"

        cli_main()

        assert os.path.isfile(output_path)

        with open(output_path) as json_file:
            json_response = json.load(json_file)

        assert VIEW_HOST_JSON["result"] == json_response

        # Cleanup
        os.remove(output_path)

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "view",
            "8.8.8.8",
            "--index-type",
            "hosts",
            "--format",
            "screen",
        ]
        + CensysTestCase.cli_args,
    )
    def test_write_screen(self):
        self.responses.add(
            responses.GET,
            V2_URL + "/hosts/8.8.8.8",
            status=200,
            json=VIEW_HOST_JSON,
        )

        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        json_response = json.loads(temp_stdout.getvalue().strip())

        assert VIEW_HOST_JSON["result"] == json_response

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "view",
            "8.8.8.8",
            "--index-type",
            "hosts",
            "--format",
            "json",
            "--at-time",
            "2021-05-20",
        ]
        + CensysTestCase.cli_args,
    )
    def test_at_time(self):
        self.responses.add(
            responses.GET,
            V2_URL + "/hosts/8.8.8.8?at_time=2021-05-20T00%3A00%3A00.000000Z",
            status=200,
            json=VIEW_HOST_JSON,
        )

        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        cli_response = temp_stdout.getvalue().strip()
        assert cli_response.startswith(WROTE_PREFIX)

        json_path = cli_response.replace(WROTE_PREFIX, "").strip()
        assert json_path.endswith(".json")
        assert "2021-05-20" in json_path
        assert "censys-view-8.8.8.8." in json_path

        with open(json_path) as json_file:
            json_response = json.load(json_file)

        assert VIEW_HOST_JSON["result"] == json_response

        # Cleanup
        os.remove(json_path)

    @patch(
        "argparse._sys.argv",
        ["censys", "view", "8.8.8.8", "--open"] + CensysTestCase.cli_args,
    )
    @patch("censys.cli.commands.search.webbrowser.open")
    def test_open(self, mock_open):
        cli_main()
        mock_open.assert_called_with("https://search.censys.io/hosts/8.8.8.8")
