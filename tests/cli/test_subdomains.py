import contextlib
import json
from io import StringIO
from typing import Set
from unittest.mock import patch

import responses
from parameterized import parameterized

from tests.utils import V1_URL, CensysTestCase

from censys.cli import main as cli_main
from censys.cli.commands import subdomains

TEST_DOMAINS = {
    "help.censys.io",
    "lp.censys.io",
    "about.censys.io",
    "fast.github.com",
}


def search_callback(request):
    payload = json.loads(request.body)
    resp_body = {
        "results": [{"parsed.names": list(TEST_DOMAINS)}],
        "metadata": {"page": payload["page"], "pages": 100},
    }
    return (200, {}, json.dumps(resp_body))


class CensysCliSubdomainsTest(CensysTestCase):
    @parameterized.expand(
        [
            (True,),
            (False,),
        ]
    )
    def test_print_subdomains(
        self,
        test_json_bool: bool,
        test_subdomains: Set[str] = TEST_DOMAINS,
    ):
        # Mock
        mock_print_json = self.mocker.patch("censys.cli.utils.console.print_json")
        mock_print = self.mocker.patch("censys.cli.utils.console.print")

        # Actual call
        subdomains.print_subdomains(test_subdomains, test_json_bool)

        # Assertions
        if test_json_bool:
            mock_print_json.assert_called_once()
        else:
            for subdomain in test_subdomains:
                mock_print.assert_any_call(f"  - {subdomain}")

    # one that tests core logic of search (searching right string) (done)
    # make sure it prints out in a list (done)
    # testing json - (json_loads) check to make sure output json is the same one from search
    # mock censys certificates .search function

    @patch(
        "argparse._sys.argv",
        ["censys", "subdomains", "censys.io"] + CensysTestCase.cli_args,
    )
    def test_search_subdomains(self):
        # Test data
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

        for line in cli_response.split("\n"):
            assert "censys.io" in line
