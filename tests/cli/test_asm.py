import contextlib
import json
import os.path
from io import StringIO

import pytest
import responses
from responses.matchers import json_params_matcher

from tests.asm.utils import V1_URL
from tests.utils import CensysTestCase

from censys.cli import main as cli_main
from censys.cli.commands.asm import get_seeds_from_xml

SEEDS_JSON = [
    {"value": 0, "type": "ASN"},
    {"value": 0, "type": "IP_ADDRESS"},
    {"value": 0, "type": "DOMAIN_NAME"},
    {"value": 0, "type": "CIDR"},
]
XML_SEEDS = [
    {"value": "45.33.32.156", "type": "IP_ADDRESS"},
    {"value": "scanme.nmap.org", "type": "DOMAIN_NAME"},
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
TEST_XML_PATH = os.path.join(os.path.dirname(__file__), "test.xml")


class CensysASMCliTest(CensysTestCase):
    def setUp(self):
        super().setUp()

    def test_add_seeds(self):
        # Mock
        self.patch_args(
            ["censys", "asm", "add-seeds", "-j", json.dumps(SEEDS_JSON)], asm_auth=True
        )
        self.responses.add(
            responses.POST,
            V1_URL + "/seeds",
            status=200,
            json=ADD_SEEDS_JSON,
        )

        temp_stdout = StringIO()
        # Actual call
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()
        # Assertions
        assert "Added 4 seeds" in temp_stdout.getvalue()

    def test_add_seeds_no_type(self):
        # Mock
        self.patch_args(
            ["censys", "asm", "add-seeds", "-j", json.dumps(["1.1.1.1"])], asm_auth=True
        )
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
        # Actual call
        cli_main()

    def test_add_seeds_multi_type(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "add-seeds",
                "-j",
                json.dumps(
                    [
                        {"value": "1.1.1.1"},
                        {"value": "192.168. 0.15/24", "type": "CIDR"},
                    ]
                ),
            ],
            asm_auth=True,
        )
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
        # Actual call
        cli_main()

    def test_add_seeds_from_stdin(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "add-seeds",
                "-i",
                "-",
            ],
            asm_auth=True,
        )
        self.mocker.patch(
            "sys.stdin",
            StringIO(
                json.dumps(
                    [
                        {"value": "1.1.1.1"},
                        {"value": "192.168. 0.15/24", "type": "CIDR"},
                    ]
                )
            ),
        )
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
        # Actual call
        cli_main()

    def test_add_seeds_from_file(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "add-seeds",
                "-i",
                "test.json",
            ],
            asm_auth=True,
        )
        self.mocker.patch(
            "builtins.open",
            new_callable=self.mocker.mock_open,
            read_data=json.dumps(
                [{"value": "1.1.1.1"}, {"value": "192.168.0.15/24", "type": "CIDR"}]
            ),
        )
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
                            {"value": "192.168.0.15/24", "type": "CIDR", "label": ""},
                        ]
                    }
                )
            ],
        )
        # Actual call
        cli_main()

    def test_add_seeds_invalid_json(self):
        # Mock
        self.patch_args(
            ["censys", "asm", "add-seeds", "-j", "<html><div>not json</div>"],
            asm_auth=True,
        )
        # Actual call/error raising
        with pytest.raises(SystemExit, match="1"):
            cli_main()

    def test_add_seeds_bad_json(self):
        # Mock
        self.patch_args(
            ["censys", "asm", "add-seeds", "-j", json.dumps([12345])], asm_auth=True
        )
        temp_stdout = StringIO()
        # Actual call
        with pytest.raises(SystemExit, match="1"), contextlib.redirect_stdout(
            temp_stdout
        ):
            cli_main()
        # Assertions
        assert "Invalid seed" in temp_stdout.getvalue()

    def test_add_seeds_partial(self):
        # Mock
        self.patch_args(
            ["censys", "asm", "add-seeds", "-j", json.dumps(SEEDS_JSON)], asm_auth=True
        )
        partial_json = ADD_SEEDS_JSON.copy()
        partial_json["addedSeeds"] = partial_json["addedSeeds"][1:]
        self.responses.add(
            responses.POST,
            V1_URL + "/seeds",
            status=200,
            json=partial_json,
        )

        temp_stdout = StringIO()
        # Actual call
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()
        # Assertions
        assert "Added 3 seeds" in temp_stdout.getvalue()
        assert "Seeds not added: 1" in temp_stdout.getvalue()

    def test_add_seeds_none(self):
        # Mock
        self.patch_args(
            ["censys", "asm", "add-seeds", "-j", json.dumps(SEEDS_JSON)], asm_auth=True
        )
        partial_json = ADD_SEEDS_JSON.copy()
        partial_json["addedSeeds"] = []
        self.responses.add(
            responses.POST,
            V1_URL + "/seeds",
            status=200,
            json=partial_json,
        )

        temp_stdout = StringIO()

        # Actual call
        with pytest.raises(SystemExit, match="1"), contextlib.redirect_stdout(
            temp_stdout
        ):
            cli_main()

        # Assertions
        assert (
            "No seeds were added. (Run with -v to get more info)"
            in temp_stdout.getvalue()
        )

    def test_get_seeds_from_xml(self):
        # Actual call
        seeds = get_seeds_from_xml(str(TEST_XML_PATH))

        # Assertions
        assert seeds == XML_SEEDS

    def test_add_seeds_from_xml_file(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "add-seeds",
                "--nmap-xml",
                str(TEST_XML_PATH),
            ],
            asm_auth=True,
        )
        self.responses.add(
            responses.POST,
            V1_URL + "/seeds",
            status=200,
            json=ADD_SEEDS_JSON,
            match=[
                json_params_matcher(
                    {
                        "seeds": [
                            {
                                "value": "45.33.32.156",
                                "type": "IP_ADDRESS",
                                "label": "",
                            },
                            {
                                "value": "scanme.nmap.org",
                                "type": "DOMAIN_NAME",
                                "label": "",
                            },
                        ]
                    }
                )
            ],
        )
        # Actual call
        cli_main()

    def test_add_seeds_from_invalid_xml_file(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "add-seeds",
                "--nmap-xml",
                str(TEST_XML_PATH),
            ],
            asm_auth=True,
        )
        self.mocker.patch(
            "xml.etree.ElementTree.open",
            new_callable=self.mocker.mock_open,
            read_data="<html><div>not xml</div>",
        )

        # Actual call
        with pytest.raises(SystemExit, match="1"):
            cli_main()
