"""Censys CLI utilities."""
import csv
import json
import time
from typing import List, Tuple, Any, MutableMapping, Optional

Fields = List[str]
Results = List[dict]


def flatten(d: MutableMapping, parent_key: str = "", sep: str = ".") -> dict:
    """Generates new flattened dict from nested dict.

    Args:
        d (MutableMapping): Nested dict.
        parent_key (str): Optional; Parent key (for recursion).
        sep (str): Optional; Key seperator. Defaults to ".".

    Returns:
        dict: Flattened dict.
    """
    items: List[Tuple[str, Any]] = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


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

    print(f"Wrote results to file {file_path}")


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

    print(f"Wrote results to file {file_path}")


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
        file_name_ext = f"{time.time()}.{file_format}"
        file_path = f"censys-query-output.{file_name_ext}"

    if file_format == "json":
        return _write_json(file_path, results_list)
    if file_format == "csv":
        return _write_csv(file_path, results_list, fields=csv_fields)
    return _write_screen(results_list)
