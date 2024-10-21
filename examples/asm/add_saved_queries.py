"""Add a saved query."""

from censys.asm import SavedQueries

# Create an instance of the SavedQueries class
saved_queries = SavedQueries()

# Add a saved query
query = "host.services.http.response.body: /.*test.*/"
query_name = "Test Query"
res = saved_queries.add_saved_query(query, query_name)

# Print the added saved query
print(res)
