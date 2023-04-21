"""Censys CLI."""

from tap import Tap

from .commands import (
    AccountParser,
    AddSeedsParser,
    ConfigParser,
    HnriParser,
    SearchParser,
    SubdomainsParser,
    ViewParser,
)
from censys.common.version import __version__


class CensysCLIParser(Tap):
    """Censys CLI."""

    version: bool = False
    """Print the version and exit."""

    def configure(self) -> None:
        """Configure the CLI."""

        def help(args: "CensysCLIParser") -> None:
            args.print_help()

        self.set_defaults(func=help)
        self.add_subparsers(help="sub-command help")
        self.add_subparser("account", AccountParser)
        self.add_subparser("add-seeds", AddSeedsParser)
        self.add_subparser("config", ConfigParser)
        self.add_subparser("hnri", HnriParser)
        self.add_subparser("search", SearchParser)
        self.add_subparser("subdomains", SubdomainsParser)
        self.add_subparser("view", ViewParser)

        self.add_argument("-v", "--version", action="store_true")


def parse_args() -> CensysCLIParser:
    """Parse command line arguments.

    Returns:
        The parsed arguments.
    """
    parser = CensysCLIParser()
    return parser.parse_args()


def main() -> None:
    """Main cli function."""
    args = parse_args()

    if args.version:
        print(f"Censys Python Version: {__version__}")
        args.exit(0)

    try:
        args.func(args)
    except KeyboardInterrupt:  # pragma: no cover
        args.exit(1)
