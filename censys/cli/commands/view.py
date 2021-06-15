"""Censys view CLI."""
import argparse
import webbrowser

from ..utils import write_file
from censys.search import SearchClient


def cli_view(args: argparse.Namespace):
    """Search subcommand.

    Args:
        args (Namespace): Argparse Namespace.
    """
    if args.open:
        return webbrowser.open(
            f"https://search.censys.io/{args.index_type}/{args.document_id}"
        )

    censys_args = {}

    if args.api_id:
        censys_args["api_id"] = args.api_id

    if args.api_secret:
        censys_args["api_secret"] = args.api_secret

    c = SearchClient(**censys_args)

    index = getattr(c.v2, args.index_type)

    view_args = {}
    write_args = {
        "file_format": args.format,
        "file_path": args.output,
        "base_name": f"censys-view-{args.document_id}",
    }

    if args.at_time:
        view_args["at_time"] = args.at_time
        write_args["time_str"] = args.at_time.strftime("%Y-%m-%d")

    document = index.view(args.document_id, **view_args)

    try:
        write_file(document, **write_args)
    except ValueError as error:  # pragma: no cover
        print(f"Error writing log file. Error: {error}")
