import csv
import time
import json
from typing import Union, Optional, List

from censys.ipv4 import CensysIPv4
from censys.websites import CensysWebsites
from censys.certificates import CensysCertificates
from censys.exceptions import CensysCLIException

Fields = List[str]
Results = List[dict]
Index = Union[CensysIPv4, CensysWebsites, CensysCertificates]


class CensysAPISearch:
    """
    This class searches the Censys API, taking in options from the command line and
    returning the results to a CSV or JSON file, or to stdout.

    Args:
        api_id (str, optional): The API ID provided by Censys.
        api_secret (str, optional): The API secret provided by Censys.
        start_page (int, optional): Page number to start from. Defaults to 1.
        max_pages (int, optional): The maximum number of pages. Defaults to 10.
    """

    csv_fields: Fields = list()
    """A list of fields to be used by the CSV writer."""

    def __init__(self, **kwargs):
        self.api_user = kwargs.get("api_id")
        self.api_pass = kwargs.get("api_secret")
        self.start_page = kwargs.get("start_page", 1)
        self.max_pages = kwargs.get("max_pages", 10)

    @staticmethod
    def _write_csv(file_path: str, search_results: Results, fields: Fields) -> bool:
        """
        This method writes the search results to a new file in CSV format.

        Args:
            file_path (str): Name of the file to write to on the disk.
            search_results (Results): A list of results from the query.
            fields (Fields): A list of fields to write as headers.

        Returns:
            bool: True if wrote to file successfully.
        """

        with open(file_path, "w") as output_file:
            if search_results and isinstance(search_results, list):
                # Get the header row from the first result
                writer = csv.DictWriter(output_file, fieldnames=fields)
                writer.writeheader()

                for result in search_results:
                    # Use the Dict writer to process and write results to CSV
                    writer.writerow(result)

        print(f"Wrote results to file {file_path}")

        # method returns True, if the file has been written successfully.
        return True

    @staticmethod
    def _write_json(file_path: str, search_results: Results) -> bool:
        """
        This method writes the search results to a new file in JSON format.

        Args:
            file_path (str): Name of the file to write to on the disk.
            search_results (Results): A list of results from the query.

        Returns:
            bool: True if wrote to file successfully.
        """

        with open(file_path, "w") as output_file:
            # Since the results are already in JSON, just write them to a file.
            json.dump(search_results, output_file, indent=4)

        print(f"Wrote results to file {file_path}")
        return True

    @staticmethod
    def _write_screen(search_results: Results) -> bool:
        """
        This method writes the search results to screen.

        Args:
            search_results (Results): A list of results from the query.

        Returns:
            bool: True if wrote to file successfully.
        """

        print(json.dumps(search_results, indent=4))
        return True

    def write_file(
        self,
        results_list: Results,
        file_format: str = "screen",
        file_path: Optional[str] = None,
    ) -> bool:
        """
        This method just sorts which format will be used to store
        the results of the query.

        Args:
            results_list (Results): A list of results from the API query.
            file_format (str, optional): The format of the output.
            file_path (str optional): A path to write results to.

        Returns:
            bool: True if wrote out successfully.
        """

        if file_format and isinstance(file_format, str):
            file_format = file_format.lower()

        if not file_path:
            # This method just creates some dynamic file names
            file_name_ext = f"{time.time()}.{file_format}"
            file_path = f"censys-query-output.{file_name_ext}"

        if file_format == "json":
            return self._write_json(file_path, results_list)
        if file_format == "csv":
            return self._write_csv(file_path, results_list, fields=self.csv_fields)
        return self._write_screen(results_list)

    def _combine_fields(
        self, default_fields: Fields, user_fields: Fields, overwrite: bool = False,
    ) -> Fields:
        """
        This method is used to specify which fields will be returned in the results.

        Args:
            default_fields (Fields): A list of fields that are returned by default.
            user_fields (Fields): A list of user-specified fields. Max 20.
            overwrite (bool, optional): Whether to overwrite or append default fields
                                        with user fields. Defaults to False.

        Raises:
            CensysCLIException: Too many fields specified.

        Returns:
            Fields: A list of fields.
        """

        field_list: Fields = default_fields

        if user_fields:
            if overwrite:
                field_list = user_fields
            else:
                field_list = list(set(user_fields + default_fields))

        # This is the hard limit for the number of fields that can be in a query.
        if len(list(field_list)) > 20:
            raise CensysCLIException(
                "Too many fields specified. The maximum number of fields is 20."
            )

        self.csv_fields = list(field_list)
        return list(field_list)

    def _process_search(
        self, query: str, search_index: Index, fields: Fields
    ) -> Results:
        """
        This method provides a common way to process searches from the API.

        Args:
            query (str): The string to send to the API as a query.
            search_index (Index): The data set to be queried.
            fields (Fields): A list of fields to be returned for each result.

        Returns:
            Results: A list of results from the query.
        """

        records = []

        while True:
            response = search_index.paged_search(
                query=query, fields=fields, page=self.start_page
            )

            for record in response["results"]:
                records.append(record)

            # Break while loop when last page is reached
            if (
                response["metadata"]["page"] >= response["metadata"]["pages"]
                or response["metadata"]["page"] >= self.max_pages
            ):
                break

            self.start_page += 1

        return records

    def search_ipv4(self, **kwargs) -> Results:
        """
        A method to search the IPv4 data set via the API.

        Args:
            query (str): The string search query.
            fields (list, optional): The fields that should be returned with a query.
            overwrite (bool, optional): Whether to overwrite or append default fields
                                        with user fields. Defaults to False.

        Returns:
            Results: A list of results from the query.
        """

        default_fields = [
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
        ]

        query = kwargs.get("query", "")
        fields = kwargs.get("fields", [])
        overwrite = kwargs.get("overwrite", False)

        index = CensysIPv4(api_id=self.api_user, api_secret=self.api_pass)

        return self._process_search(
            query,
            index,
            self._combine_fields(default_fields, fields, overwrite=overwrite),
        )

    def search_certificates(self, **kwargs) -> Results:
        """
        A method to search the Certificates data set via the API.

        Args:
            query (str): The string search query.
            fields (list, optional): The fields that should be returned with a query.
            overwrite (bool, optional): Whether to overwrite or append default fields
                                        with user fields. Defaults to False.

        Returns:
            Results: A list of results from the query.
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
        overwrite = kwargs.get("overwrite", False)

        index = CensysCertificates(api_id=self.api_user, api_secret=self.api_pass)

        return self._process_search(
            query,
            index,
            self._combine_fields(default_fields, fields, overwrite=overwrite),
        )

    def search_websites(self, **kwargs) -> Results:
        """
        A method to search the Websites (Alexa Top 1M) data set via the API.

        Args:
            query (str): The string search query.
            fields (list, optional): The fields that should be returned with a query.
            overwrite (bool, optional): Whether to overwrite or append default fields
                                        with user fields. Defaults to False.

        Returns:
            Results: A list of results from the query.
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
        overwrite = kwargs.get("overwrite", False)

        index = CensysWebsites(api_id=self.api_user, api_secret=self.api_pass)

        return self._process_search(
            query,
            index,
            self._combine_fields(default_fields, fields, overwrite=overwrite),
        )
