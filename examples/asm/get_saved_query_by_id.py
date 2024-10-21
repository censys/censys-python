"""Get a saved query by ID."""

from censys.asm import SavedQueries

# Create an instance of the SavedQueries class
saved_queries = SavedQueries()

# Get the saved query by ID
query_id = "query_id"
query = saved_queries.get_saved_query_by_id(query_id)

# Print the saved query
print(query)
