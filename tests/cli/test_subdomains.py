import contextlib
from io import StringIO
from typing import Set

import responses
from parameterized import parameterized

from tests.utils import V2_URL, CensysTestCase

from censys.cli import main as cli_main
from censys.cli.commands import subdomains

TEST_DOMAINS = {
    "help.censys.io",
    "lp.censys.io",
    "about.censys.io",
    "fast.github.com",
}

CERT_SEARCH_RESPONSE = {
    "result": {
        "total": len(TEST_DOMAINS),
        "hits": [{"names": [name]} for name in TEST_DOMAINS],
        "links": {},
    },
}


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

    def test_search_subdomains(self):
        # Mock
        self.responses.add(
            responses.POST,
            V2_URL + "/certificates/search",
            json=CERT_SEARCH_RESPONSE,
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
