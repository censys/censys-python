"""Censys Account CLI Commands."""

from tap import Tap

from censys.common.config import load_config


class AccountParser(Tap):
    """Censys Account CLI Parser.

    Please note that currently, the Censys CLI only supports the Search Account API.
    """

    profile: str = "default"
    """The profile to use."""

    json: bool = False
    """Print the account information as JSON."""

    def configure(self) -> None:
        """Configure the CLI."""

        def account(args: "AccountParser") -> None:
            """Print the account information.

            Args:
                args: The parsed arguments.
            """
            config = load_config()
            if args.profile not in config.search_profiles:
                args.exit(1, f"Profile {args.profile} not found.")
            profile = config.search_profiles[args.profile]
            # TODO: Implement Search Account API

        self.set_defaults(func=account)
        self.add_argument("-p", "--profile", help="The profile to use.")
        self.add_argument(
            "-j",
            "--json",
            action="store_true",
            help="Print the account information as JSON.",
        )
