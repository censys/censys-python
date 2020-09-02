#!/usr/bin/env python
from __future__ import absolute_import

import argparse
import csv
import json
import os
import time

from censys.ipv4 import CensysIPv4
from censys.certificates import CensysCertificates
from censys.websites import CensysWebsites


class CensysAPISearch:

    csv_fields = []

    def __init__(self, **kwargs):
        """
        This class searches the Censys API, taking in options from the command line and returning the results to a CSV or
        JSON file, or to stdout.

        Args:
            kwargs:
                format: what format to write the results. CSV, JSON, or stdout.
                start_page: what page the query should start from.
                max_pages: adjust the number of results returned by the API. Currently, 100 results per page.
                censys_api_secret: The API secret provided by Censys. Can also be provided as an environmental variable.
                censys_api_id: The API id provided by Censys. Can also be provided as an environmental variable.
        """

        self.api_user = os.getenv("CENSYS_API_ID", kwargs.get("censys_api_id", "xxxx"))
        self.api_pass = os.getenv(
            "CENSYS_API_SECRET", kwargs.get("censys_api_secret", "xxxx")
        )

        self.output_format = kwargs.get("format", "json")
        self.start_page = kwargs.get("start_page", 1)
        self.max_pages = kwargs.get("max_pages", 10)

    def _write_csv(self, filename, search_results):
        """
        This method writes the search results to a new file in CSV format.

        Args:
            filename: Is the name of the file to write to on the disk.
            search_results: Is a list of results from the API query.
        """

        try:
            # Open a new file for writing results.
            with open(filename, "w") as output_file:

                if search_results and type(search_results) is list:

                    # Get the header row from the first result
                    fields = self.csv_fields
                    writer = csv.DictWriter(output_file, fieldnames=fields)
                    writer.writeheader()

                    for result in search_results:
                        # Use the Dict writer to process the results and write them into CSV
                        writer.writerow(result)

            print("Wrote results to file {}".format(filename))

            # method returns True, if the file has been written successfully.
            return True

        except Exception as e:
            print("error writing log file. Error: {}".format(e))
            # Returns False if the file could not complete the write.
            return False

    def _write_json(self, filename, search_results):
        """
        This method writes the search results to a new file in JSON format.

        Args:
            filename: Is the name of the file to write to on the disk.
            search_results: Is a list of results from the API query.
        """
        try:
            with open(filename, "w") as output_file:

                # Since the results are already in JSON format, just write the results to a file.
                output_file.write(json.dumps(search_results, indent=4))

            print("Wrote results to file {}".format(filename))
            return True

        except Exception as e:
            print("Error writing JSON. Error: {}".format(e))
            return False

    def _write_screen(self, search_results):
        """
        This method writes the search results to screen.

        Args:
            search_results: Is a list of results from the API query.
        """
        print(json.dumps(search_results, indent=4))
        return True

    def write_file(self, results_list):
        """
        This method just sorts which format will be used to store the results of the query.

        Args:
            results_list: Is a list of results from the API query.
        """

        # This method just creates some dynamic file names
        file_name_ext = "{}.{}".format(time.time(), self.output_format)
        filename = "{}.{}".format("censys-query-output", file_name_ext)

        if self.output_format == "csv":
            return self._write_csv(filename, results_list)
        elif self.output_format == "json":
            return self._write_json(filename, results_list)
        else:
            return self._write_screen(results_list)

    def _combine_fields(self, default_fields, user_fields, append):
        """
        This method is used to combine, or exclude fields depending on what the user has requested.

        Args:
            default_fields: A list of fields that are returned by default.
            user_fields: A list of fields the user would like back.
            append: Determines whether user fields are added to default set, or returned on their own.

        """

        if append is True:
            field_list = list(set(user_fields + default_fields))
        elif append is False:
            field_list = user_fields
        else:
            field_list = default_fields

        # This is the hard limit for the number of fields that can be in a query.
        if len(list(field_list)) <= 20:
            self.csv_fields = list(field_list)
            return list(field_list)
        else:
            raise Exception(
                "Two many fields specified. Please limit the number of fields to 20 or less."
            )

    def _process_search(self, query, search_index, fields):
        """
        This method provides a common way to process searches from the API.

        Args:
            query: The string to send to the API as a query.
            search_index: The data set to be queried - IPv4, Website, or Certificates
            fields: A list of fields that should be returned.
        """

        records = []

        while True:
            r = search_index.paged_search(
                query=query, fields=fields, page=self.start_page
            )

            for record in r["results"]:
                records.append(record)

            if (
                r["metadata"]["page"] >= r["metadata"]["pages"]
                or r["metadata"]["page"] >= self.max_pages
            ):
                break
            else:
                self.start_page += 1

        return records

    def search_ipv4(self, **kwargs):
        """
        A method to search the IPv4 data set via the API

        Args:
            query: The string search query.
            fields: The fields that should be returned with a query
            append: Determines user fields are added to the default field list, or returned on their own.
        """

        default_fields = [
            "updated_at",
            "protocols",
            "metadata.description",
            "autonomous_system.name",
            "23.telnet.banner",
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
        ]

        query = kwargs.get("query", "")
        fields = kwargs.get("fields", [])
        append = kwargs.get("append", True)

        c = CensysIPv4(api_id=self.api_user, api_secret=self.api_pass)

        return self._process_search(
            query, c, self._combine_fields(default_fields, fields, append)
        )

    def search_certificates(self, **kwargs):
        """
        A method to search the Certificates data set via the API

        Args:
            query: The string search query.
            fields: The fields that should be returned with a query
            append: Determines user fields are added to the default field list, or returned on their own.
        """

        default_fields = [
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
        ]

        query = kwargs.get("query", "")
        fields = kwargs.get("fields", [])
        append = kwargs.get("append", True)

        c = CensysCertificates(api_id=self.api_user, api_secret=self.api_pass)

        return self._process_search(
            query, c, self._combine_fields(default_fields, fields, append)
        )

    def search_websites(self, **kwargs):
        """
        A method to search the Websites (Alexa Top 1M) data set via the API

        Args:
            query: The string search query.
            fields: The fields that should be returned with a query
            append: Determines user fields are added to the default field list, or returned on their own.
        """

        default_fields = [
            "443.https.tls.version",
            "alexa_rank",
            "domain",
            "ports",
            "protocols",
            "tags",
            "updated_at",
        ]

        query = kwargs.get("query", "")
        fields = kwargs.get("fields", [])
        append = kwargs.get("append", True)

        c = CensysWebsites(api_id=self.api_user, api_secret=self.api_pass)

        return self._process_search(
            query, c, self._combine_fields(default_fields, fields, append)
        )


def main():
    """
        Argparse - Mistakes were made...
    """

    parser = argparse.ArgumentParser(
        description="Search The Censys Data Set via the command line"
    )

    parser.add_argument("query", type=str)
    parser.add_argument("--fields", nargs="+")
    parser.add_argument(
        "--query_type",
        default="ipv4",
        metavar="ipv4|certs|websites",
        choices=["ipv4", "certs", "websites"],
    )
    parser.add_argument(
        "--append",
        help="Append the given list of fields to the default fields",
        type=str,
        choices=["true", "false"],
    )
    parser.add_argument("--output", default="screen", metavar="json|csv|screen")
    parser.add_argument("--start_page", default=1, type=int)
    parser.add_argument("--max_pages", default=1, type=int)
    parser.add_argument(
        "--censys_api_id",
        required=False,
        metavar="XXXXXXXXXX",
        help="(optional) You must provide your Censys API ID here or as an environmental variable CENSYS_API_ID",
    )
    parser.add_argument(
        "--censys_api_secret",
        required=False,
        metavar="XXXXXXXXXX",
        help="(optional) You must provide your Censys API SECRET here or as an environmental variable CENSYS_API_SECRET",
    )

    args = parser.parse_args()

    censys_args = {"query": args.query}

    if args.fields:
        censys_args["fields"] = args.fields

    if args.output:
        censys_args["format"] = args.output

    if args.start_page:
        censys_args["start_page"] = args.start_page

    if args.max_pages:
        censys_args["max_pages"] = args.max_pages

    if args.censys_api_id:
        censys_args["censys_api_id"] = args.censys_api_id

    if args.censys_api_secret:
        censys_args["censys_api_secret"] = args.censys_api_secret

    if args.append:

        if args.append.lower() == "false":
            censys_args["append"] = False
        elif args.append.lower == "true":
            censys_args["append"] = True

    censys = CensysAPISearch(**censys_args)

    if args.query_type == "ipv4":
        censys.write_file(censys.search_ipv4(**censys_args))

    if args.query_type == "certs":
        censys.write_file(censys.search_certificates(**censys_args))

    if args.query_type == "websites":
        censys.write_file(censys.search_websites(**censys_args))


if __name__ == "__main__":

    main()
