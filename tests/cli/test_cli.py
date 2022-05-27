import contextlib
from io import StringIO

import pytest

from tests.utils import CensysTestCase

from censys.cli import main as cli_main
from censys.cli.commands import __all__ as cli_commands
from censys.common import __version__


class CensysCliTest(CensysTestCase):
    def test_default_help(self):
        # Mock
        self.patch_args(["censys"])
        temp_stdout = StringIO()
        # Actual call
        with contextlib.redirect_stdout(temp_stdout), pytest.raises(SystemExit):
            cli_main()
        # Assertions
        assert temp_stdout.getvalue().strip().startswith("usage: censys")

    def test_help(self):
        # Mock
        self.patch_args(["censys", "--help"])
        temp_stdout = StringIO()
        # Actual call
        with contextlib.redirect_stdout(temp_stdout), pytest.raises(SystemExit):
            cli_main()

        stdout = temp_stdout.getvalue().strip()
        # Assertions
        assert stdout.startswith("usage: censys")
        assert "{" + ",".join(sorted(cli_commands)) + "}" in stdout
        assert "-v, --version" in stdout

    def test_version(self):
        # Mock
        self.patch_args(["censys", "-v"])
        temp_stdout = StringIO()
        # Actual call
        with contextlib.redirect_stdout(temp_stdout), pytest.raises(SystemExit):
            cli_main()
        # Assertion
        assert __version__ in temp_stdout.getvalue()
