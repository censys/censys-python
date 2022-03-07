"""Add seeds in bulk from CSV file."""
import csv

from censys.asm import Seeds

s = Seeds()

seeds_to_add = []

# Read CSV file
# Example CSV file (headers are required):
# type,value,label
# IP_ADDRESS,1.1.1.1,"Optional label"
# DOMAIN_NAME,example.com,
with open("seeds.csv") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        seed = {
            "type": row.get("type"),
            "value": row.get("value"),
            "label": row.get("label"),
        }
        seeds_to_add.append(seed)

s.add_seeds(seeds_to_add)
