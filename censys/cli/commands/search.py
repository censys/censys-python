"""Censys search CLI."""
import argparse
import webbrowser
from typing import List
from urllib.parse import urlencode

from ..utils import V1_INDEXES, V2_INDEXES, console, write_file
from censys.common.exceptions import CensysCLIException
from censys.search import SearchClient

Fields = List[str]
Results = List[dict]

DEFAULT_FIELDS = {
    "ipv4": [
        "updated_at",
        "protocols",
        "metadata.description",
        "autonomous_system.name",
        "23.telnet.banner.banner",
        "80.http.get.title",
        "80.http.get.metadata.description",
        "8080.http.get.metadata.description",
        "8888.http.get.metadata.description",
        "443.https.get.metadata.description",
        "443.https.get.title",
        "443.https.tls.certificate.parsed.subject_dn",
        "443.https.tls.certificate.parsed.names",
        "443.https.tls.certificate.parsed.subject.common_name",
        "443.https.tls.certificate.parsed.extensions.subject_alt_name.dns_names",
    ],
    "certs": [
        "metadata.updated_at",
        "parsed.issuer.common_name",
        "parsed.names",
        "parsed.serial_number",
        "parsed.self_signed",
        "parsed.subject.common_name",
        "parsed.validity.start",
        "parsed.validity.end",
        "parsed.validity.length",
        "metadata.source",
        "metadata.seen_in_scan",
        "tags",
    ],
    "websites": [
        "443.https.tls.version",
        "alexa_rank",
        "domain",
        "ports",
        "protocols",
        "tags",
        "updated_at",
    ],
}


def cli_search(args: argparse.Namespace):
    """Search subcommand.

    Args:
        args (Namespace): Argparse Namespace.
    """
    index_type = args.index_type or args.query_type

    if args.open:
        url_query = {"q": args.query}
        if index_type in V1_INDEXES:
            if index_type == "certs":
                index_type = "certificates"
            return webbrowser.open(
                f"https://censys.io/{index_type}?{urlencode(url_query)}"
            )
        elif index_type in V2_INDEXES:
            url_query.update({"resource": index_type})
            return webbrowser.open(
                f"https://search.censys.io/search?{urlencode(url_query)}"
            )

    censys_args = {}

    if args.api_id:
        censys_args["api_id"] = args.api_id

    if args.api_secret:
        censys_args["api_secret"] = args.api_secret

    c = SearchClient(**censys_args)

    search_args = {}
    write_args = {"file_format": args.format, "file_path": args.output}

    if index_type in V1_INDEXES:
        index = getattr(c.v1, index_type)

        if args.max_records:
            search_args["max_records"] = args.max_records

        fields: Fields = []
        if args.fields:
            if args.overwrite:
                fields = args.fields
            else:
                fields = args.fields + DEFAULT_FIELDS[index_type]
                # Remove duplicates
                fields = list(set(fields))
            write_args["csv_fields"] = fields

        if len(fields) > 20:
            raise CensysCLIException(
                "Too many fields specified. The maximum number of fields is 20."
            )

        search_args["fields"] = fields

        with console.status("Searching"):
            results = list(index.search(args.query, **search_args))
    elif index_type in V2_INDEXES:
        if args.format == "csv":
            raise CensysCLIException(
                "The CSV file format is not valid for Search 2.0 responses."
            )
        index = getattr(c.v2, index_type)

        if args.pages:
            search_args["pages"] = args.pages

        with console.status("Searching"):
            query = index.search(args.query, **search_args)

            results = []
            for hits in query:
                results += hits

    try:
        write_file(results, **write_args)
    except ValueError as error:  # pragma: no cover
        print(f"Error writing log file. Error: {error}")
