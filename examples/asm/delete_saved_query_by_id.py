"""Delete a saved query by ID."""

from censys.asm import SavedQueries

# Create an instance of the SavedQueries class
saved_queries = SavedQueries()

# Delete the saved query by ID
query_id = "query_id"
saved_queries.delete_saved_query_by_id(query_id)
