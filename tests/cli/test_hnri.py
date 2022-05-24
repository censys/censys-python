import contextlib
from io import StringIO
from ipaddress import ip_address
from unittest.mock import patch

import pytest
import responses

from tests.search.v2.test_hosts import VIEW_HOST_JSON
from tests.utils import V2_URL, CensysTestCase

from censys.cli import main as cli_main
from censys.cli.commands.hnri import CensysHNRI
from censys.common.exceptions import CensysCLIException


class CensysCliHNRITest(CensysTestCase):
    IPIFY_URL = "https://api.ipify.org?format=json"
    IP_ADDRESS = "8.8.8.8"

    def setUp(self):
        super().setUp()
        self.api = CensysHNRI(self.api_id, self.api_secret)

    def test_hnri_medium(self):
        # Mock 
        self.patch_args(["censys", "hnri"], search_auth=True)
        mock_ip = self.mocker.patch("censys.cli.commands.hnri.CensysHNRI.get_current_ip", return_value = self. IP_ADDRESS)
        # Setup response 
        response = VIEW_HOST_JSON.copy()
        response["result"]["services"] = [
            {"port": 443, "service_name": "HTTPS"},
            {"port": 53, "service_name": "DNS"},
        ]
        self.responses.add(
            responses.GET,
            f"{V2_URL}/hosts/{self.IP_ADDRESS}",
            status=200,
            json=response,
        )

        temp_stdout = StringIO()
        # Actual call 
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        stdout = temp_stdout.getvalue().strip()
        # Assertions 
        assert mock_ip.return_value in stdout
        assert "Medium Risks Found" in stdout
        assert "HTTPS" in stdout
        assert "443" in stdout
        assert "DNS" in stdout
        assert "53" in stdout

    def test_hnri_no_medium(self):
        self.patch_args(["censys", "hnri"], search_auth=True)
        # Mock 
        mock_ip = self.mocker.patch( "censys.cli.commands.hnri.CensysHNRI.get_current_ip", return_value = self.IP_ADDRESS)
        # Setup response 
        response = VIEW_HOST_JSON.copy()
        response["result"]["services"] = [{"port": 23, "service_name": "VNC"}]
        self.responses.add(
            responses.GET,
            f"{V2_URL}/hosts/{self.IP_ADDRESS}",
            status=200,
            json=response,
        )

        temp_stdout = StringIO()
        # Actual call 
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        stdout = temp_stdout.getvalue().strip()
        # Assertions 
        assert mock_ip.return_value in stdout
        assert "High Risks Found" in stdout
        assert "VNC" in stdout
        assert "23" in stdout
        assert "You don't have any Medium Risks in your network" in stdout

 
    def test_hnri_not_found(self):
        self.patch_args(["censys", "hnri"], search_auth=True)
        # Mock
        mock_ip = self.mocker.patch("censys.cli.commands.hnri.CensysHNRI.get_current_ip", return_value = self.IP_ADDRESS)
        # Setup response 
        response = VIEW_HOST_JSON.copy()
        response["result"]["services"] = []
        self.responses.add(
            responses.GET,
            f"{V2_URL}/hosts/{self.IP_ADDRESS}",
            status=200,
            json=response,
        )

        temp_stdout = StringIO()
        # Actual Call 
        with contextlib.redirect_stdout(temp_stdout):
            cli_main()

        stdout = temp_stdout.getvalue().strip()
        # Assertions 
        assert mock_ip.return_value in stdout
        assert "No Risks were found on your network" in stdout

    def test_get_current_ip(self):
        # Setup response 
        self.responses.add(
            responses.GET,
            self.IPIFY_URL,
            status=200,
            json={"ip": self.IP_ADDRESS},
        )
        # Actual call 
        ip_address = self.api.get_current_ip()
        # Assertions
        assert ip_address == self.IP_ADDRESS

    def test_no_risks(self):
        # Actual call/error raising 
        with pytest.raises(CensysCLIException):
            self.api.risks_to_string([], [])

  
    def test_open(self):
        self.patch_args(["censys", "hnri", "--open"])
        # Mock 
        mock_open = self.mocker.patch("censys.cli.commands.view.webbrowser.open")
        # Actual call/error raising
        with pytest.raises(SystemExit, match="0"):
            cli_main()
        # Assertions 
        mock_open.assert_called_with("https://search.censys.io/me")
