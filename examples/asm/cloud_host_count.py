"""Retrieve host counts by cloud since the first day of 2021."""
from datetime import date

from censys import AsmClient

c = AsmClient()

count = c.clouds.get_host_counts(date(2021, 1, 1))
print(count)
