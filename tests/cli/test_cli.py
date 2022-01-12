import contextlib
from io import StringIO
from unittest.mock import patch

import pytest

from tests.utils import CensysTestCase

from censys.cli import main as cli_main
from censys.cli.commands import __all__ as cli_commands
from censys.common import __version__


class CensysCliTest(CensysTestCase):
    @patch("argparse._sys.argv", ["censys"])
    def test_default_help(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout), pytest.raises(SystemExit):
            cli_main()

        assert temp_stdout.getvalue().strip().startswith("usage: censys")

    @patch("argparse._sys.argv", ["censys", "--help"])
    def test_help(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout), pytest.raises(SystemExit):
            cli_main()

        stdout = temp_stdout.getvalue().strip()
        assert stdout.startswith("usage: censys")
        assert "{" + ",".join(sorted(cli_commands)) + "}" in stdout
        assert "-v, --version" in stdout

    @patch("argparse._sys.argv", ["censys", "-v"])
    def test_version(self):
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout), pytest.raises(SystemExit):
            cli_main()

        assert __version__ in temp_stdout.getvalue()
