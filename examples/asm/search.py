"""Execute a saved query by ID."""
from censys.asm import InventorySearch

# Create an instance of the SavedQueries class
inventory_search = InventorySearch()

# Delete the saved query by ID
query = "query"
res = inventory_search.search(query=query)

print(res)
