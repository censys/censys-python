import contextlib
import json
from io import StringIO
from unittest.mock import patch

import pytest
import responses

from tests.search.v1.test_api import ACCOUNT_JSON
from tests.utils import V1_URL, CensysTestCase

from censys.cli import main as cli_main


class CensysCliAccountTest(CensysTestCase):
    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "account",
        ]
        + CensysTestCase.cli_args,
    )
    def test_table(self):
        self.responses.add(
            responses.GET,
            V1_URL + "/account",
            status=200,
            json=ACCOUNT_JSON,
        )

        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout), pytest.raises(
            SystemExit, match="0"
        ):
            cli_main()

        cli_response = temp_stdout.getvalue().strip()
        assert ACCOUNT_JSON["email"] in cli_response
        assert ACCOUNT_JSON["login"] in cli_response
        quota = ACCOUNT_JSON["quota"]
        assert f"{quota['used']} / {quota['allowance']}" in cli_response

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "account",
            "--json",
        ]
        + CensysTestCase.cli_args,
    )
    def test_json(self):
        self.responses.add(
            responses.GET,
            V1_URL + "/account",
            status=200,
            json=ACCOUNT_JSON,
        )

        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout), pytest.raises(
            SystemExit, match="0"
        ):
            cli_main()

        cli_response = temp_stdout.getvalue().strip()
        assert ACCOUNT_JSON == json.loads(cli_response)
