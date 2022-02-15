import contextlib
import json
from io import StringIO
from unittest.mock import mock_open, patch

import pytest
import responses
from responses.matchers import json_params_matcher

from tests.asm.utils import V1_URL
from tests.utils import CensysTestCase

from censys.cli import main as cli_main

SEEDS_JSON = [
    {"value": 0, "type": "ASN"},
    {"value": 0, "type": "IP_ADDRESS"},
    {"value": 0, "type": "DOMAIN_NAME"},
    {"value": 0, "type": "CIDR"},
]
ADD_SEEDS_JSON = {
    "addedSeeds": [
        {
            "source": "API",
            "createdOn": "string",
            "id": 0,
            "type": "ASN",
            "value": 0,
            "label": "string",
        },
        {
            "source": "API",
            "createdOn": "string",
            "id": 0,
            "type": "IP_ADDRESS",
            "value": "string",
            "label": "string",
        },
        {
            "source": "API",
            "createdOn": "string",
            "id": 0,
            "type": "DOMAIN_NAME",
            "value": "string",
            "label": "string",
        },
        {
            "source": "API",
            "createdOn": "string",
            "id": 0,
            "type": "CIDR",
            "value": "string",
            "label": "string",
        },
    ],
    "skippedReservedSeeds": ["string", 0],
}


class CensysASMCliTest(CensysTestCase):
    def setUp(self):
        super().setUp()

    @patch(
        "argparse._sys.argv",
        ["censys", "asm", "add-seeds", "-j", json.dumps(SEEDS_JSON)]
        + CensysTestCase.asm_cli_args,
    )
    def test_add_seeds(self):
        self.responses.add(
            responses.POST,
            V1_URL + "/seeds",
            status=200,
            json=ADD_SEEDS_JSON,
        )

        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()
            assert "Added 4 seeds" in temp_stdout.getvalue()

    @patch(
        "argparse._sys.argv",
        ["censys", "asm", "add-seeds", "-j", json.dumps(["1.1.1.1"])]
        + CensysTestCase.asm_cli_args,
    )
    def test_add_seeds_no_type(self):
        self.responses.add(
            responses.POST,
            V1_URL + "/seeds",
            status=200,
            json=ADD_SEEDS_JSON,
            match=[
                json_params_matcher(
                    {"seeds": [{"value": "1.1.1.1", "type": "IP_ADDRESS", "label": ""}]}
                )
            ],
        )

        cli_main()

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "asm",
            "add-seeds",
            "-j",
            json.dumps(
                [{"value": "1.1.1.1"}, {"value": "192.168. 0.15/24", "type": "CIDR"}]
            ),
        ]
        + CensysTestCase.asm_cli_args,
    )
    def test_add_seeds_multi_type(self):
        self.responses.add(
            responses.POST,
            V1_URL + "/seeds",
            status=200,
            json=ADD_SEEDS_JSON,
            match=[
                json_params_matcher(
                    {
                        "seeds": [
                            {"value": "1.1.1.1", "type": "IP_ADDRESS", "label": ""},
                            {"value": "192.168. 0.15/24", "type": "CIDR", "label": ""},
                        ]
                    }
                )
            ],
        )

        cli_main()

    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "asm",
            "add-seeds",
            "-i",
            "-",
        ]
        + CensysTestCase.asm_cli_args,
    )
    @patch(
        "sys.stdin",
        StringIO(
            json.dumps(
                [{"value": "1.1.1.1"}, {"value": "192.168. 0.15/24", "type": "CIDR"}]
            )
        ),
    )
    def test_add_seeds_from_stdin(self):
        self.responses.add(
            responses.POST,
            V1_URL + "/seeds",
            status=200,
            json=ADD_SEEDS_JSON,
            match=[
                json_params_matcher(
                    {
                        "seeds": [
                            {"value": "1.1.1.1", "type": "IP_ADDRESS", "label": ""},
                            {"value": "192.168. 0.15/24", "type": "CIDR", "label": ""},
                        ]
                    }
                )
            ],
        )

        cli_main()

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=json.dumps(
            [{"value": "1.1.1.1"}, {"value": "192.168. 0.15/24", "type": "CIDR"}]
        ),
    )
    @patch(
        "argparse._sys.argv",
        [
            "censys",
            "asm",
            "add-seeds",
            "-i",
            "test.json",
        ]
        + CensysTestCase.asm_cli_args,
    )
    def test_add_seeds_from_file(self, mock_file):
        self.responses.add(
            responses.POST,
            V1_URL + "/seeds",
            status=200,
            json=ADD_SEEDS_JSON,
            match=[
                json_params_matcher(
                    {
                        "seeds": [
                            {"value": "1.1.1.1", "type": "IP_ADDRESS", "label": ""},
                            {"value": "192.168. 0.15/24", "type": "CIDR", "label": ""},
                        ]
                    }
                )
            ],
        )

        cli_main()

    @patch(
        "argparse._sys.argv",
        ["censys", "asm", "add-seeds", "-j", "<html><div>not json</div>"]
        + CensysTestCase.asm_cli_args,
    )
    def test_add_seeds_invalid_json(self):
        with pytest.raises(SystemExit, match="1"):
            cli_main()

    @patch(
        "argparse._sys.argv",
        ["censys", "asm", "add-seeds", "-j", json.dumps([12345])]
        + CensysTestCase.asm_cli_args,
    )
    def test_add_seeds_bad_json(self):
        temp_stdout = StringIO()
        with pytest.raises(SystemExit, match="1"), contextlib.redirect_stdout(
            temp_stdout
        ):
            cli_main()

        assert "Invalid seed" in temp_stdout.getvalue()

    @patch(
        "argparse._sys.argv",
        ["censys", "asm", "add-seeds", "-j", json.dumps(SEEDS_JSON)]
        + CensysTestCase.asm_cli_args,
    )
    def test_add_seeds_partial(self):
        partial_json = ADD_SEEDS_JSON.copy()
        partial_json["addedSeeds"] = partial_json["addedSeeds"][1:]
        self.responses.add(
            responses.POST,
            V1_URL + "/seeds",
            status=200,
            json=partial_json,
        )

        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        assert "Added 3 seeds" in temp_stdout.getvalue()
        assert "Seeds not added: 1" in temp_stdout.getvalue()

    @patch(
        "argparse._sys.argv",
        ["censys", "asm", "add-seeds", "-j", json.dumps(SEEDS_JSON)]
        + CensysTestCase.asm_cli_args,
    )
    def test_add_seeds_none(self):
        partial_json = ADD_SEEDS_JSON.copy()
        partial_json["addedSeeds"] = []
        self.responses.add(
            responses.POST,
            V1_URL + "/seeds",
            status=200,
            json=partial_json,
        )

        temp_stdout = StringIO()
        with pytest.raises(SystemExit, match="1"), contextlib.redirect_stdout(
            temp_stdout
        ):
            cli_main()

        assert (
            "No seeds were added. (Run with -v to get more info)"
            in temp_stdout.getvalue()
        )
