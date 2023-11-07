import contextlib
import json
import os.path
from io import StringIO

import pytest
import responses
from responses import matchers
from responses.matchers import json_params_matcher

from tests.asm.utils import V1_URL
from tests.cli.test_config import TEST_CONFIG_PATH
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

GET_SEEDS_JSON = {
    "seeds": [
        {
            "id": 1,
            "type": "ASN",
            "value": 0,
            "label": "Test",
            "source": "API",
            "createdOn": "2022-11-01T12:34:23.111142Z",
        },
        {
            "id": 2,
            "type": "IP_ADDRESS",
            "value": "1.2.3.4",
            "label": "Test",
            "source": "API",
            "createdOn": "2022-11-01T12:34:23.111142Z",
        },
        {
            "id": 3,
            "type": "DOMAIN_NAME",
            "value": "foo.com",
            "label": "Test",
            "source": "API",
            "createdOn": "2022-11-01T12:34:23.111142Z",
        },
        {
            "id": 4,
            "type": "CIDR",
            "value": "200.200.200.0/24",
            "label": "Test",
            "source": "API",
            "createdOn": "2022-11-01T12:34:23.111142Z",
        },
        {
            "id": 5,
            "type": "IP_ADDRESS",
            "value": "5.6.7.8",
            "label": "Test 2",
            "source": "API",
            "createdOn": "2022-11-01T12:34:23.111142Z",
        },
    ]
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

        # Actual call
        temp_stdout = StringIO()
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

    def test_add_seeds_from_file_json(self):
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
                [
                    {"value": "1.1.1.1"},
                    {"value": "192.168.0.15/24", "type": "CIDR"},
                ]
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

    def test_add_seeds_from_file_csv(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "add-seeds",
                "--csv",
                "-i",
                "seeds.csv",
            ],
            asm_auth=True,
        )
        # Just to make sure we're reading from the fake file
        self.mocker.patch("censys.common.config.CONFIG_PATH", TEST_CONFIG_PATH)
        self.mocker.patch(
            "builtins.open",
            new_callable=self.mocker.mock_open,
            read_data="\n".join(
                ["type,value", "IP_ADDRESS,1.1.1.1", "CIDR,192.168.0.15/24"]
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

        # Actual call
        temp_stdout = StringIO()
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

        # Actual call
        temp_stdout = StringIO()
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

        # Actual call
        temp_stdout = StringIO()
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

    def test_delete_all_seeds_force_one_seed(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "delete-all-seeds",
                "--force",
            ],
            asm_auth=True,
        )
        self.responses.add(
            responses.GET,
            V1_URL + "/seeds",
            status=200,
            json={
                "seeds": [
                    item
                    for item in GET_SEEDS_JSON["seeds"]
                    if item["value"] == "1.2.3.4"
                ]
            },
            match=[matchers.query_param_matcher({})],
        )
        self.responses.add(
            responses.DELETE,
            V1_URL + "/seeds/2",
            status=200,
            match=[matchers.query_param_matcher({})],
        )

        # Actual call
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        # Assertions
        assert len(self.responses.calls) == 2  # make sure both requests were seen
        assert "Deleted 1 of 1 total seeds." in temp_stdout.getvalue()

    def test_delete_all_seeds_force(self):
        # Mock
        #
        # The idea is that delete-all-seeds will call GET to get seeds, we'll give it back the
        # two IP_ADDRESS seeds (just to cut down the list to test), and then we should see it call
        # DELETE on each of the seed IDs we gave it back, and then it will report on the number of
        # seeds deleted
        #
        self.patch_args(
            [
                "censys",
                "asm",
                "delete-all-seeds",
                "--force",
            ],
            asm_auth=True,
        )
        self.responses.add(
            responses.GET,
            V1_URL + "/seeds",
            status=200,
            json={
                "seeds": [
                    item
                    for item in GET_SEEDS_JSON["seeds"]
                    if item["type"] == "IP_ADDRESS"
                ]
            },
            match=[matchers.query_param_matcher({})],
        )
        self.responses.add(
            responses.DELETE,
            V1_URL + "/seeds/2",
            status=200,
            match=[matchers.query_param_matcher({})],
        )
        self.responses.add(
            responses.DELETE,
            V1_URL + "/seeds/5",
            status=200,
            match=[matchers.query_param_matcher({})],
        )

        # Actual call
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        # Assertions
        assert len(self.responses.calls) == 3  # make sure all three requests were seen
        assert "Deleted 2 of 2 total seeds." in temp_stdout.getvalue()

    def test_delete_all_seeds_yes(self):
        # Mock
        #
        # The idea is that delete-all-seeds will call GET to get seeds, we'll give it back the
        # two IP_ADDRESS seeds (just to cut down the list to test), and then we should see it call
        # DELETE on each of the seed IDs we gave it back, and then it will report on the number of
        # seeds deleted
        #
        self.patch_args(
            [
                "censys",
                "asm",
                "delete-all-seeds",
            ],
            asm_auth=True,
        )
        self.responses.add(
            responses.GET,
            V1_URL + "/seeds",
            status=200,
            json={
                "seeds": [
                    item
                    for item in GET_SEEDS_JSON["seeds"]
                    if item["type"] == "IP_ADDRESS"
                ]
            },
            match=[matchers.query_param_matcher({})],
        )
        self.responses.add(
            responses.DELETE,
            V1_URL + "/seeds/2",
            status=200,
            match=[matchers.query_param_matcher({})],
        )
        self.responses.add(
            responses.DELETE,
            V1_URL + "/seeds/5",
            status=200,
            match=[matchers.query_param_matcher({})],
        )
        self.mocker.patch(
            "builtins.input", side_effect=["y"]
        )  # answer 'y' to are you sure

        # Actual call
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        # Assertions
        assert len(self.responses.calls) == 3  # make sure all three requests were seen
        assert "Deleted 2 of 2 total seeds." in temp_stdout.getvalue()

    def test_delete_all_seeds_no(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "delete-all-seeds",
            ],
            asm_auth=True,
        )
        self.mocker.patch("builtins.input", side_effect=["n"])

        # Actual call
        with pytest.raises(SystemExit, match="1"):
            cli_main()

    def test_delete_seeds_by_ip(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "delete-seeds",
                "-j",
                json.dumps(["1.2.3.4", "5.6.7.8", "9.9.9.9"]),
            ],
            asm_auth=True,
        )
        self.responses.add(
            responses.GET,
            V1_URL + "/seeds",
            status=200,
            json=GET_SEEDS_JSON,
            match=[matchers.query_param_matcher({})],
        )
        self.responses.add(
            responses.DELETE,
            V1_URL + "/seeds/2",
            status=200,
            match=[matchers.query_param_matcher({})],
        )
        self.responses.add(
            responses.DELETE,
            V1_URL + "/seeds/5",
            status=200,
            match=[matchers.query_param_matcher({})],
        )

        # Actual call
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        # Assertions
        assert len(self.responses.calls) == 3  # make sure all three requests were seen
        assert (
            "Deleted 2 seeds.\nUnable to delete 1 seeds because they were not present.\n"
            in temp_stdout.getvalue()
        )

    def test_delete_seed_by_id(self):
        # Mock
        self.patch_args(
            ["censys", "asm", "delete-seeds", "-j", json.dumps([{"id": 2}])],
            asm_auth=True,
        )
        self.responses.add(
            responses.GET,
            V1_URL + "/seeds",
            status=200,
            json=GET_SEEDS_JSON,
            match=[matchers.query_param_matcher({})],
        )
        self.responses.add(
            responses.DELETE,
            V1_URL + "/seeds/2",
            status=200,
            match=[matchers.query_param_matcher({})],
        )

        # Actual call
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        # Assertions
        assert len(self.responses.calls) == 2  # make sure all three requests were seen
        assert "Deleted 1 seeds." in temp_stdout.getvalue()

    def test_delete_seeds_by_id(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "delete-seeds",
                "-j",
                json.dumps([{"id": 2}, {"id": 5}]),
            ],
            asm_auth=True,
        )
        self.responses.add(
            responses.GET,
            V1_URL + "/seeds",
            status=200,
            json=GET_SEEDS_JSON,
            match=[matchers.query_param_matcher({})],
        )
        self.responses.add(
            responses.DELETE,
            V1_URL + "/seeds/2",
            status=200,
            match=[matchers.query_param_matcher({})],
        )
        self.responses.add(
            responses.DELETE,
            V1_URL + "/seeds/5",
            status=200,
            match=[matchers.query_param_matcher({})],
        )

        # Actual call
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        # Assertions
        assert len(self.responses.calls) == 3  # make sure all three requests were seen
        assert "Deleted 2 seeds." in temp_stdout.getvalue()

    def test_delete_seeds_by_csv(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "delete-seeds",
                "--csv",
                "-i",
                "seeds.csv",
            ],
            asm_auth=True,
        )
        # Just to make sure we're reading from the fake file
        self.mocker.patch("censys.common.config.CONFIG_PATH", TEST_CONFIG_PATH)
        self.mocker.patch(
            "builtins.open",
            new_callable=self.mocker.mock_open,
            read_data="\n".join(
                [
                    "type,value",
                    "IP_ADDRESS,1.2.3.4",
                    "CIDR,200.200.200.0/24"
                ]
            ),
        )

        self.responses.add(
            responses.GET,
            V1_URL + "/seeds",
            status=200,
            json=GET_SEEDS_JSON,
            match=[matchers.query_param_matcher({})],
        )
        self.responses.add(
            responses.DELETE,
            V1_URL + "/seeds/2",
            status=200,
            match=[matchers.query_param_matcher({})],
        )
        self.responses.add(
            responses.DELETE,
            V1_URL + "/seeds/4",
            status=200,
            match=[matchers.query_param_matcher({})],
        )

        # Actual call
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        # Assertions
        assert len(self.responses.calls) == 3  # make sure all three requests were seen
        assert "Deleted 2 seeds." in temp_stdout.getvalue()

    def test_delete_seeds_by_asm_csv(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "delete-seeds",
                "--csv",
                "-i",
                "seeds.csv",
            ],
            asm_auth=True,
        )
        # Just to make sure we're reading from the fake file
        self.mocker.patch("censys.common.config.CONFIG_PATH", TEST_CONFIG_PATH)
        self.mocker.patch(
            "builtins.open",
            new_callable=self.mocker.mock_open,
            read_data="\n".join(
                [
                    "Type,Value",
                    "IP_ADDRESS,1.2.3.4",
                    "CIDR,200.200.200.0/24"
                ]
            ),
        )

        self.responses.add(
            responses.GET,
            V1_URL + "/seeds",
            status=200,
            json=GET_SEEDS_JSON,
            match=[matchers.query_param_matcher({})],
        )
        self.responses.add(
            responses.DELETE,
            V1_URL + "/seeds/2",
            status=200,
            match=[matchers.query_param_matcher({})],
        )
        self.responses.add(
            responses.DELETE,
            V1_URL + "/seeds/4",
            status=200,
            match=[matchers.query_param_matcher({})],
        )

        # Actual call
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        # Assertions
        assert len(self.responses.calls) == 3  # make sure all three requests were seen
        assert "Deleted 2 seeds." in temp_stdout.getvalue()

    def test_delete_seeds_nonexistent_id(self):
        # Mock
        self.patch_args(
            ["censys", "asm", "delete-seeds", "-j", json.dumps([{"id": 100}])],
            asm_auth=True,
        )
        self.responses.add(
            responses.GET,
            V1_URL + "/seeds",
            status=200,
            json=GET_SEEDS_JSON,
            match=[matchers.query_param_matcher({})],
        )
        self.responses.add(
            responses.DELETE,
            V1_URL + "/seeds/100",
            status=404,
            match=[matchers.query_param_matcher({})],
            body=json.dumps(
                {
                    "message": "Unable to Find Seed",
                    "errorCode": 10014,
                    "details": [{"id": 100}],
                }
            ),
        )

        # Actual call
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        # Assertions
        assert len(self.responses.calls) == 2  # make sure all three requests were seen
        assert (
            "Deleted 0 seeds.\nUnable to delete 1 seeds because they were not present.\n"
            in temp_stdout.getvalue()
        )

    def test_delete_seeds_multiple_nonexistent_id(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "delete-seeds",
                "-j",
                json.dumps([{"id": 100}, {"id": 101}]),
            ],
            asm_auth=True,
        )
        self.responses.add(
            responses.GET,
            V1_URL + "/seeds",
            status=200,
            json=GET_SEEDS_JSON,
            match=[matchers.query_param_matcher({})],
        )
        self.responses.add(
            responses.DELETE,
            V1_URL + "/seeds/100",
            status=404,
            match=[matchers.query_param_matcher({})],
            body=json.dumps(
                {
                    "message": "Unable to Find Seed",
                    "errorCode": 10014,
                    "details": [{"id": 100}],
                }
            ),
        )
        self.responses.add(
            responses.DELETE,
            V1_URL + "/seeds/101",
            status=404,
            match=[matchers.query_param_matcher({})],
            body=json.dumps(
                {
                    "message": "Unable to Find Seed",
                    "errorCode": 10014,
                    "details": [{"id": 101}],
                }
            ),
        )

        # Actual call
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        # Assertions
        assert len(self.responses.calls) == 3  # make sure all three requests were seen
        assert (
            "Deleted 0 seeds.\nUnable to delete 2 seeds because they were not present.\n"
            in temp_stdout.getvalue()
        )

    def test_delete_seeds_no_id_or_ip(self):
        # Mock
        self.patch_args(
            ["censys", "asm", "delete-seeds", "-j", json.dumps([{"foo": 100}])],
            asm_auth=True,
        )
        self.responses.add(
            responses.GET,
            V1_URL + "/seeds",
            status=200,
            json=GET_SEEDS_JSON,
            match=[matchers.query_param_matcher({})],
        )

        # Actual call
        temp_stdout = StringIO()
        with pytest.raises(SystemExit, match="0"), contextlib.redirect_stdout(
            temp_stdout
        ):
            cli_main()

        # Assertions
        assert (
            "Error, no seed id or value for seed.\nNo seeds to delete.\n"
            in temp_stdout.getvalue()
        )

    def test_delete_labeled_seeds(self):
        # Mock
        self.patch_args(
            ["censys", "asm", "delete-labeled-seeds", "--label", "Test"], asm_auth=True
        )
        self.responses.add(
            responses.DELETE,
            V1_URL + "/seeds",
            status=200,
            json=GET_SEEDS_JSON,
            match=[matchers.query_param_matcher({"label": "Test"})],
        )

        # Actual call
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        # Assertions
        assert 'Deleted seeds with label "Test".\n' in temp_stdout.getvalue()

    def test_delete_labeled_seeds_without_label(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "delete-labeled-seeds",
            ],
            asm_auth=True,
        )

        # Actual call
        with pytest.raises(SystemExit, match="2"):
            cli_main()

    def test_replace_labeled_seeds(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "replace-labeled-seeds",
                "--label",
                "Test",
                "-j",
                json.dumps(
                    [
                        {"value": "1.1.1.1"},
                        {"value": "192.168. 0.15/24", "type": "CIDR", "label": "Test Label"},
                    ]
                ),
            ],
            asm_auth=True,
        )
        self.responses.add(
            responses.PUT,
            V1_URL + "/seeds",
            status=200,
            json={
                "removedSeeds": [],
                "skippedReservedSeeds": [],
                "addedSeeds": [
                    {
                        "id": 100,
                        "value": "1.1.1.1",
                        "type": "IP_ADDRESS",
                    },
                    {
                        "id": 101,
                        "value": "192.168. 0.15/24",
                        "type": "CIDR",
                    },
                ],
            },
            match=[matchers.query_param_matcher({"label": "Test", "force": True})],
        )

        # Actual call
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        # Assertions
        assert (
            "Removed 0 seeds.  Added 2 seeds.  Skipped 0 reserved seeds."
            in temp_stdout.getvalue()
        )

    def test_replace_labeled_seeds_without_label(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "replace-labeled-seeds",
            ],
            asm_auth=True,
        )

        # Actual call
        with pytest.raises(SystemExit, match="2"):
            cli_main()

    def test_list_seeds_json(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "list-seeds",
            ],
            asm_auth=True,
        )
        self.responses.add(
            responses.GET,
            V1_URL + "/seeds",
            status=200,
            json=GET_SEEDS_JSON,
            match=[matchers.query_param_matcher({})],
        )

        temp_stdout = StringIO()

        # Actual call
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        # Assertions
        actual_json = json.loads(temp_stdout.getvalue())
        assert actual_json == GET_SEEDS_JSON["seeds"]

    def test_list_seeds_csv(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "list-seeds",
                "--csv",
            ],
            asm_auth=True,
        )
        self.responses.add(
            responses.GET,
            V1_URL + "/seeds",
            status=200,
            json=GET_SEEDS_JSON,
            match=[matchers.query_param_matcher({})],
        )

        # Actual call
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        # Assertions
        expected_output = (
            "\n".join(
                [
                    "id,type,value,label,source,createdOn",
                    "1,ASN,0,Test,API,2022-11-01T12:34:23.111142Z",
                    "2,IP_ADDRESS,1.2.3.4,Test,API,2022-11-01T12:34:23.111142Z",
                    "3,DOMAIN_NAME,foo.com,Test,API,2022-11-01T12:34:23.111142Z",
                    "4,CIDR,200.200.200.0/24,Test,API,2022-11-01T12:34:23.111142Z",
                    "5,IP_ADDRESS,5.6.7.8,Test 2,API,2022-11-01T12:34:23.111142Z",
                ]
            )
            + "\n"
        )
        assert expected_output in temp_stdout.getvalue()

    def test_list_seeds_type_ip(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "list-seeds",
                "--type",
                "IP_ADDRESS",
                "--csv",
            ],
            asm_auth=True,
        )
        self.responses.add(
            responses.GET,
            V1_URL + "/seeds",
            status=200,
            json={
                "seeds": [
                    item
                    for item in GET_SEEDS_JSON["seeds"]
                    if item["type"] == "IP_ADDRESS"
                ]
            },
            match=[matchers.query_param_matcher({"type": "IP_ADDRESS"})],
        )

        # Actual call
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        # Assertions
        expected_output = (
            "\n".join(
                [
                    "id,type,value,label,source,createdOn",
                    "2,IP_ADDRESS,1.2.3.4,Test,API,2022-11-01T12:34:23.111142Z",
                    "5,IP_ADDRESS,5.6.7.8,Test 2,API,2022-11-01T12:34:23.111142Z",
                ]
            )
            + "\n"
        )
        assert expected_output in temp_stdout.getvalue()

    def test_list_seeds_label_test(self):
        # Mock
        self.patch_args(
            [
                "censys",
                "asm",
                "list-seeds",
                "--label",
                "Test",
                "--csv",
            ],
            asm_auth=True,
        )
        self.responses.add(
            responses.GET,
            V1_URL + "/seeds",
            status=200,
            json={
                "seeds": [
                    item for item in GET_SEEDS_JSON["seeds"] if item["label"] == "Test"
                ]
            },
            match=[matchers.query_param_matcher({"label": "Test"})],
        )

        # Actual call
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        # Assertions
        expected_output = (
            "\n".join(
                [
                    "id,type,value,label,source,createdOn",
                    "1,ASN,0,Test,API,2022-11-01T12:34:23.111142Z",
                    "2,IP_ADDRESS,1.2.3.4,Test,API,2022-11-01T12:34:23.111142Z",
                    "3,DOMAIN_NAME,foo.com,Test,API,2022-11-01T12:34:23.111142Z",
                    "4,CIDR,200.200.200.0/24,Test,API,2022-11-01T12:34:23.111142Z",
                ]
            )
            + "\n"
        )
        assert expected_output in temp_stdout.getvalue()
