import csv
import argparse
from pathlib import Path
from typing import List, Set

import netaddr

from censys.base import CensysAPIBase


class CensysAdminMaxmind(CensysAPIBase):
    def upload(self, collection: str, version: int, records: List[Set[dict]]):
        url = "/admin/maxmind/%s/%i" % (collection, version)
        return self._post(url, data={"records": records})

    def delete(self, collection: str, version: int):
        url = "/admin/maxmind/%s/%i" % (collection, version)
        return self._delete(url)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("collection")
    parser.add_argument("version", type=int)
    parser.add_argument("locations_path", metavar="locations.csv", type=Path)
    parser.add_argument("blocks_path", metavar="blocks.csv", type=Path)
    args = parser.parse_args()

    collection = args.collection
    version = args.version

    censys = CensysAdminMaxmind()

    to_upload = []
    # population dictionary with all the details for a geoid
    locations = {}
    headers = [
        "geoname_id",
        "locale_code",
        "continent_code",
        "continent_name",
        "country_iso_code",
        "country_name",
        "subdivision_1_iso_code",
        "subdivision_1_name",
        "subdivision_2_iso_code",
        "subdivision_2_name",
        "city_name",
        "metro_code",
        "time_zone",
    ]
    with open(args.locations_path, "r") as locations_file:
        for row in csv.reader(locations_file):
            if not row:
                continue
            if row[0].startswith("geoname_id"):
                continue
            locations[row[0]] = {k: v for (k, v) in zip(headers, row)}
    # now that all geoid data is in memory, go through ips, generate full
    # records and then upload them in batches to Censys.
    headers = [
        "network",
        "geoname_id",
        "registered_country_geoname_id",
        "represented_country_geoname_id",
        "is_anonymous_proxy",
        "is_satellite_provider",
        "postal_code",
        "latitude",
        "longitude",
    ]
    with open(args.blocks_path, "r") as blocks_file:
        for row in csv.reader(blocks_file):
            if not row:
                continue
            if row[0].startswith("network"):
                continue
            ip_details = {k: v for (k, v) in zip(headers, row)}
            geoid = row[1]
            if geoid == "":
                geoid = row[2]
            details = locations[geoid]
            cidr = netaddr.IPNetwork(row[0])
            first = int(cidr[0])
            last = int(cidr[-1])
            rec = {"ip_begin": first, "ip_end": last}
            rec.update(ip_details)
            rec.update(details)
            print(rec)
            to_upload.append(rec)
            if len(to_upload) > 10000:
                censys.upload(collection, version, to_upload)
                to_upload = []
        censys.upload(collection, version, to_upload)


if __name__ == "__main__":
    main()
