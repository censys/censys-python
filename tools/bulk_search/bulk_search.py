import sys
import os
import json
import time
import argparse

# Censys client import (only used when not mock)
try:
    from censys.search import CensysHosts
except ImportError:
    CensysHosts = None


def bulk_search(input_file, output_file, mock=False):
    results = []

    if not mock and CensysHosts is None:
        print("[!] Censys library missing or not installed properly.")
        mock = True

    if not mock:
        api_id = os.getenv("CENSYS_API_ID")
        api_secret = os.getenv("CENSYS_API_SECRET")
        if not api_id or not api_secret:
            print("[!] Missing API credentials. Switching to mock mode.")
            mock = True

        if not mock:
            h = CensysHosts(api_id=api_id, api_secret=api_secret)

    print("\n=== Bulk Search Started ===")
    with open(input_file, "r") as targets:
        for ip in targets:
            ip = ip.strip()
            if not ip:
                continue

            print(f"[+] Searching: {ip}")
            try:
                if mock:
                    # Generate mock result
                    result = {
                        "ip": ip,
                        "status": "mock-result-success",
                        "open_ports": [80, 443],
                        "tech": ["nginx", "ssl"]
                    }
                else:
                    # Actual search request (will fail on free tier)
                    result = list(h.search(f"ip:{ip}", per_page=1))

                results.append(result)

            except Exception as e:
                print(f"[!] Error: {e}")
                time.sleep(1)
                continue

    with open(output_file, "w") as out:
        json.dump(results, out, indent=4)

    print(f"\n[✔] Results written to {output_file}")
    print("=== Done ===\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bulk Censys Search Tool")

    parser.add_argument("-f", "--file", required=True, help="Input file containing IP list")
    parser.add_argument("-o", "--output", required=True, help="Output JSON file")
    parser.add_argument("--mock", action="store_true", help="Enable mock mode (no API calls)")

    args = parser.parse_args()

    bulk_search(args.file, args.output, args.mock)
