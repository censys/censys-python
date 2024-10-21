"""Edit a saved query by ID."""

from censys.asm import SavedQueries

# Create an instance of the SavedQueries class
saved_queries = SavedQueries()

# Edit the saved query by ID
query_id = "query_id"
query = "host.services.http.response.body: /.*test2.*/"
query_name = "Test Query 2"
res = saved_queries.edit_saved_query_by_id(query_id, query, query_name)

# Print the edited saved query
print(res)
