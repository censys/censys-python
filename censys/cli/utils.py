"""Censys CLI utilities."""
import argparse
import csv
import datetime
import json
import os.path
import time
from typing import List, Optional

from rich.console import Console

Fields = List[str]
Results = List[dict]

V1_INDEXES = ["ipv4", "certs", "websites"]
V2_INDEXES = ["hosts"]
INDEXES = V1_INDEXES + V2_INDEXES

console = Console()


def print_wrote_file(file_path: str):
    """Print wrote file confirmation.

    Args:
        file_path (str): Name of the file to write to on the disk.
    """
    abs_file_path = os.path.abspath(file_path)
    console.print(f"Wrote results to file {abs_file_path}", soft_wrap=True)


def _write_csv(file_path: str, search_results: Results, fields: Fields):
    """Write search results to a new file in CSV format.

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

    print_wrote_file(file_path)


def _write_json(file_path: str, search_results: Results):
    """Write search results to a new file in JSON format.

    Args:
        file_path (str): Name of the file to write to on the disk.
        search_results (Results): A list of results from the query.

    Returns:
        bool: True if wrote to file successfully.
    """
    with open(file_path, "w") as output_file:
        # Since the results are already in JSON, just write them to a file.
        json.dump(search_results, output_file, indent=4)

    print_wrote_file(file_path)


def _write_screen(search_results: Results):
    """Writes search results to standard output.

    Args:
        search_results (Results): A list of results from the query.

    Returns:
        bool: True if wrote to file successfully.
    """
    print(json.dumps(search_results, indent=4))


def write_file(
    results_list: Results,
    file_format: str = "screen",
    file_path: Optional[str] = None,
    time_str: str = str(time.time()),
    base_name: str = "censys-query-output",
    csv_fields: Fields = [],
):
    """Maps formats and writes results.

    Args:
        results_list (Results): A list of results from the API query.
        file_format (str): Optional; The format of the output.
        file_path (str): Optional; A path to write results to.

    Returns:
        bool: True if wrote out successfully.
    """
    if file_format and isinstance(file_format, str):
        file_format = file_format.lower()

    if not file_path:
        # This method just creates some dynamic file names
        file_path = ".".join([base_name, time_str, file_format])

    if file_format == "json":
        return _write_json(file_path, results_list)
    if file_format == "csv":
        return _write_csv(file_path, results_list, fields=csv_fields)
    return _write_screen(results_list)


def valid_datetime_type(datetime_str: str) -> datetime.datetime:
    """Custom argparse type for user datetime values from arg."""
    try:
        return datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            return datetime.datetime.strptime(datetime_str, "%Y-%m-%d")
        except ValueError:
            msg = f"Given datetime ({datetime_str}) is not valid! Expected format: 'YYYY-MM-DD' or 'YYYY-MM-DD HH:mm'."
            raise argparse.ArgumentTypeError(msg)
