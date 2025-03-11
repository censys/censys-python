#!/usr/bin/env python
"""Demo script showing how to use the Censys Platform Search API with ResultPaginator.

This script demonstrates various ways to use the ResultPaginator class
to efficiently work with paginated search results.

Usage:
    python platform_search_demo.py

Environment variables:
    CENSYS_PLATFORM_TOKEN: Your Censys Platform API token
    CENSYS_ORGANIZATION_ID: Your Censys Organization ID

To set up these variables, you can:
1. Export them in your shell:
   export CENSYS_PLATFORM_TOKEN=your_token
   export CENSYS_ORGANIZATION_ID=your_org_id

2. Or use the CLI config command:
   censys platform config
"""

import json
import os
import sys
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from censys.common.config import DEFAULT, get_config
from censys.platform import CensysSearch


def get_credentials() -> Tuple[Optional[str], Optional[str]]:
    """Get credentials from environment variables or config file.

    Returns:
        Tuple[Optional[str], Optional[str]]: API token and organization ID
    """
    # Try environment variables first
    token = os.environ.get("CENSYS_PLATFORM_TOKEN")
    org_id = os.environ.get("CENSYS_ORGANIZATION_ID")

    # If both are set, return them
    if token and org_id:
        return token, org_id

    # Try config file
    try:
        config = get_config()
        if not token:
            token = config.get(DEFAULT, "platform_token", fallback=None)
        if not org_id:
            org_id = config.get(DEFAULT, "platform_org_id", fallback=None)
    except Exception:
        # If there's an error reading config, just continue with None values
        pass

    return token, org_id


def print_result_summary(results: List[Dict], total: int, query: str):
    """Print a summary of the search results.

    Args:
        results: List of search results
        total: Total number of matching results
        query: The search query
    """
    console = Console()
    console.print(f"[bold]Query:[/bold] {query}")
    console.print(
        f"[bold]Results:[/bold] Showing {len(results)} of {total} total matches"
    )


def display_results_table(results: List[Dict], fields: List[str] = None):
    """Display results in a table format.

    Args:
        results: List of search results
        fields: Optional list of fields to display. If None, will try to detect common fields.
    """
    if not results:
        Console().print("[yellow]No results to display.[/yellow]")
        return

    # If no fields specified, try to detect common fields
    if not fields:
        # Look at the first result to determine available fields
        first_result = results[0]
        if "ip" in first_result:
            fields = ["ip", "autonomous_system.name"]
            if "services" in first_result:
                fields.append("services.port")
        elif "domain" in first_result:
            fields = ["domain", "alexa_rank"]
        else:
            # Use all top-level keys
            fields = list(first_result.keys())

    # Create table
    table = Table(title="Search Results")

    # Add columns
    for field in fields:
        # Use the field name as column title, prettified
        column_name = field.split(".")[-1].replace("_", " ").title()
        table.add_column(column_name, style="cyan")

    # Add rows
    for result in results:
        row = []
        for field in fields:
            # Handle nested fields (e.g., "autonomous_system.name")
            parts = field.split(".")
            value = result
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                elif (
                    isinstance(value, list)
                    and part == "port"
                    and parts[0] == "services"
                ):
                    # Handle services.port special case - show all ports as comma-separated list
                    ports = [
                        str(service.get("port", ""))
                        for service in result.get("services", [])
                        if "port" in service
                    ]
                    value = ", ".join(ports)
                    break
                else:
                    value = ""
                    break

            # Format the value
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            elif isinstance(value, dict):
                value = json.dumps(value, indent=2)

            row.append(str(value))

        table.add_row(*row)

    # Print table
    console = Console()
    console.print(table)


def basic_search_demo():
    """Basic search demo using the Censys Platform API."""
    console = Console()
    console.print("\n[bold blue]===== Basic Search Demo =====[/bold blue]")

    # Get credentials
    token, org_id = get_credentials()

    if not token or not org_id:
        console.print(
            "[red]Error: Missing credentials.[/red]\n"
            "Please set CENSYS_PLATFORM_TOKEN and CENSYS_ORGANIZATION_ID environment variables.\n"
            "You can also configure them using: censys platform config"
        )
        return

    # Create client
    search = CensysSearch(token=token, organization_id=org_id)

    # Simple search query
    query = "services.port:443 and services.service_name:HTTPS"
    console.print(f"Executing search: [cyan]{query}[/cyan]")

    # Method 1: Direct API query
    console.print("\n[bold]Method 1:[/bold] Direct API Query")
    results = search.query(query, per_page=5)
    hits = results["result"]["hits"]
    total = results["result"]["total"]

    print_result_summary(hits, total, query)
    display_results_table(hits, ["ip", "autonomous_system.name", "services.port"])

    # Method 2: Using get_page() for a single page
    console.print("\n[bold]Method 2:[/bold] Using get_page() for a single page")
    paginator = search.search(query, per_page=5)
    page = paginator.get_page()

    print_result_summary(page, paginator.total, query)
    display_results_table(page, ["ip", "autonomous_system.name", "services.port"])

    # Method 3: Using get_all_results() for all pages (limited to 2 for demo)
    console.print(
        "\n[bold]Method 3:[/bold] Using get_all_results() (limited to 2 pages)"
    )
    paginator = search.search(query, per_page=5, pages=2)
    all_results = paginator.get_all_results()

    print_result_summary(all_results, paginator.total, query)
    display_results_table(
        all_results, ["ip", "autonomous_system.name", "services.port"]
    )

    # Method 4: Manual iteration through pages
    console.print(
        "\n[bold]Method 4:[/bold] Manual iteration through pages (limited to 2 pages)"
    )
    paginator = search.search(query, per_page=5, pages=2)

    console.print(f"[bold]Query:[/bold] {query}")
    console.print(f"[bold]Total results:[/bold] {paginator.total}")

    for i, page in enumerate(paginator, 1):
        console.print(f"\n[bold]Page {i}[/bold] ({len(page)} results)")
        display_results_table(page, ["ip", "autonomous_system.name", "services.port"])


def search_with_fields_demo():
    """Demo showing search with specific fields."""
    console = Console()
    console.print("\n[bold blue]===== Search with Fields Demo =====[/bold blue]")

    # Get credentials
    token, org_id = get_credentials()

    if not token or not org_id:
        console.print("[red]Error: Missing credentials.[/red]")
        return

    # Create client
    search = CensysSearch(token=token, organization_id=org_id)

    # Search for HTTPS servers, but only return specific fields
    query = "services.port:443 and services.service_name:HTTPS"
    fields = ["ip", "autonomous_system.name", "autonomous_system.asn", "services.port"]

    console.print(f"Executing search with specific fields: [cyan]{query}[/cyan]")
    console.print(f"Fields: {', '.join(fields)}")

    paginator = search.search(query, per_page=5, fields=fields, pages=1)
    page = paginator.get_page()

    print_result_summary(page, paginator.total, query)
    display_results_table(page, fields)


def search_with_sorting_demo():
    """Demo showing search with sorting."""
    console = Console()
    console.print("\n[bold blue]===== Search with Sorting Demo =====[/bold blue]")

    # Get credentials
    token, org_id = get_credentials()

    if not token or not org_id:
        console.print("[red]Error: Missing credentials.[/red]")
        return

    # Create client
    search = CensysSearch(token=token, organization_id=org_id)

    # Search for HTTPS servers, sort by ASN
    query = "services.port:443 and services.service_name:HTTPS"
    fields = ["ip", "autonomous_system.name", "autonomous_system.asn", "services.port"]
    sort = "autonomous_system.asn"

    console.print(f"Executing search with sorting: [cyan]{query}[/cyan]")
    console.print(f"Sort by: {sort}")

    paginator = search.search(query, per_page=5, fields=fields, sort=sort, pages=1)
    page = paginator.get_page()

    print_result_summary(page, paginator.total, query)
    display_results_table(page, fields)


def aggregate_demo():
    """Demo showing aggregation functionality."""
    console = Console()
    console.print("\n[bold blue]===== Aggregation Demo =====[/bold blue]")

    # Get credentials
    token, org_id = get_credentials()

    if not token or not org_id:
        console.print("[red]Error: Missing credentials.[/red]")
        return

    # Create client
    search = CensysSearch(token=token, organization_id=org_id)

    # Aggregate by service name
    query = "services.port:443"
    field = "services.service_name"

    console.print(f"Executing aggregation: [cyan]{query}[/cyan]")
    console.print(f"Group by: {field}")

    result = search.aggregate(query, field, num_buckets=10)
    buckets = result["result"]["buckets"]

    # Create table
    table = Table(
        title=f"Top services on port 443 (Total: {result['result']['total']})"
    )
    table.add_column("Service Name", style="cyan")
    table.add_column("Count", style="green")
    table.add_column("Percentage", style="yellow")

    for bucket in buckets:
        percentage = (bucket["count"] / result["result"]["total"]) * 100
        table.add_row(bucket["key"], str(bucket["count"]), f"{percentage:.2f}%")

    console.print(table)


def check_credentials():
    """Check if credentials are configured and provide guidance if not.

    Returns:
        bool: True if credentials are configured, False otherwise
    """
    console = Console()
    token, org_id = get_credentials()

    if token and org_id:
        return True

    console.print(
        Panel(
            "[bold red]Error: Censys Platform credentials not found![/bold red]\n\n"
            "To use this demo, you need to configure your Censys Platform credentials.\n\n"
            "[bold]Option 1:[/bold] Set environment variables:\n"
            "    export CENSYS_PLATFORM_TOKEN=your_token\n"
            "    export CENSYS_ORGANIZATION_ID=your_organization_id\n\n"
            "[bold]Option 2:[/bold] Use the Censys CLI to configure:\n"
            "    censys platform config\n\n"
            "You can get your credentials from the Censys Platform web interface at:\n"
            "https://app.censys.io/account/api",
            title="Configuration Required",
            border_style="red",
        )
    )

    return False


if __name__ == "__main__":
    console = Console()
    console.print("[bold green]Censys Platform Search API Demo[/bold green]")
    console.print(
        "This demo shows different ways to use the ResultPaginator class "
        "for efficient pagination of search results."
    )

    # Check credentials first
    if not check_credentials():
        sys.exit(1)

    try:
        basic_search_demo()
        search_with_fields_demo()
        search_with_sorting_demo()
        aggregate_demo()
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)
