"""Get the saved queries."""

from censys.asm import SavedQueries

# Create an instance of the SavedQueries class
saved_queries = SavedQueries()

# Get the saved queries
queries = saved_queries.get_saved_queries()

# Print the saved queries
for query in queries["results"]:
    print(query)
