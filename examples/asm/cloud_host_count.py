"""Retrieve host counts by cloud since the first day of 2021."""

from datetime import date

from censys.asm import Clouds

c = Clouds()

count = c.get_host_counts(date(2021, 1, 1))
print(count)
