import contextlib
import json
from io import StringIO
from typing import Set

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


class CensysCliSubdomainsTest(CensysTestCase, TestCase):
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

    def test_search_subdomains(self):
        # Mock
        self.responses.add_callback(
            responses.POST,
            V1_URL + "/search/certificates",
            callback=search_callback,
            content_type="application/json",
        )
        self.mocker.patch(
            "argparse._sys.argv",
            ["censys", "subdomains", "censys.io"] + CensysTestCase.cli_args,
        )

        # Actual call
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        # Assertions
        mock_cli_response = temp_stdout.getvalue().strip()
        for line in mock_cli_response.split("\n"):
            assert "censys.io" in line
