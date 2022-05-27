import contextlib
import json
import os
from io import StringIO
from unittest.mock import mock_open

import pytest
import responses

from tests.cli.test_search import WROTE_PREFIX
from tests.search.v2.test_hosts import VIEW_HOST_JSON
from tests.utils import V2_URL, CensysTestCase

from censys.cli import main as cli_main
from censys.common.exceptions import CensysException


class CensysCliViewTest(CensysTestCase):
    def test_search_help(self):
        # Mock
        self.patch_args(["censys", "view", "--help"])
        temp_stdout = StringIO()
        # Actual call
        with contextlib.redirect_stdout(temp_stdout), pytest.raises(SystemExit):
            cli_main()
        # Assertions
        assert temp_stdout.getvalue().strip().startswith("usage: censys view")

    def test_no_creds(self):
        # Mock
        self.patch_args(["censys", "view", "test"])
        self.mocker.patch(
            "builtins.open", new_callable=mock_open, read_data="[DEFAULT]"
        )
        self.mocker.patch.dict(
            "os.environ", {"CENSYS_API_ID": "", "CENSYS_API_SECRET": ""}
        )
        # Actual call
        with pytest.raises(
            CensysException, match="No API ID or API secret configured."
        ):
            cli_main()

    def test_write_json(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "view",
                "8.8.8.8",
                "--index-type",
                "hosts",
                "-o",
                "censys-view-8.8.8.8.json",
            ],
            search_auth=True,
        )
        self.responses.add(
            responses.GET,
            V2_URL + "/hosts/8.8.8.8",
            status=200,
            json=VIEW_HOST_JSON,
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
        assert "censys-view-8.8.8.8." in json_path

        with open(json_path) as json_file:
            json_response = json.load(json_file)

        assert VIEW_HOST_JSON["result"] == json_response

        # Cleanup
        os.remove(json_path)

    def test_write_output_path(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "view",
                "8.8.8.8",
                "--output",
                "censys-google-dns.json",
            ],
            search_auth=True,
        )
        self.responses.add(
            responses.GET,
            V2_URL + "/hosts/8.8.8.8",
            status=200,
            json=VIEW_HOST_JSON,
        )

        output_path = "censys-google-dns.json"
        # Actual call
        cli_main()
        # Assertions
        assert os.path.isfile(output_path)

        with open(output_path) as json_file:
            json_response = json.load(json_file)

        assert VIEW_HOST_JSON["result"] == json_response

        # Cleanup
        os.remove(output_path)

    def test_write_screen(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "view",
                "8.8.8.8",
                "--index-type",
                "hosts",
            ],
            search_auth=True,
        )
        self.responses.add(
            responses.GET,
            V2_URL + "/hosts/8.8.8.8",
            status=200,
            json=VIEW_HOST_JSON,
        )

        temp_stdout = StringIO()
        # Actual call
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        json_response = json.loads(temp_stdout.getvalue().strip())
        # Assertions
        assert VIEW_HOST_JSON["result"] == json_response

    def test_at_time(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "view",
                "8.8.8.8",
                "--index-type",
                "hosts",
                "-o",
                "censys-view-8.8.8.8.json",
                "--at-time",
                "2021-05-20",
            ],
            search_auth=True,
        )
        self.responses.add(
            responses.GET,
            V2_URL + "/hosts/8.8.8.8?at_time=2021-05-20T00%3A00%3A00.000000Z",
            status=200,
            json=VIEW_HOST_JSON,
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
        assert "censys-view-8.8.8.8." in json_path

        with open(json_path) as json_file:
            json_response = json.load(json_file)

        assert VIEW_HOST_JSON["result"] == json_response

        # Cleanup
        os.remove(json_path)

    def test_open(self):
        # Mock
        self.patch_args(["censys", "view", "8.8.8.8", "--open"], search_auth=True)
        mock_open = self.mocker.patch("censys.cli.commands.view.webbrowser.open")
        # Actual call
        with pytest.raises(SystemExit, match="0"):
            cli_main()
        # Assertions
        mock_open.assert_called_with("https://search.censys.io/hosts/8.8.8.8")
