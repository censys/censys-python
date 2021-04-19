RESOURCE_PAGING_RESULTS = ["a", "b", "c", "a", "b", "c", "a", "b", "c"]
TEST_TIMEOUT = 30
TEST_SUCCESS_CODE = 200
BASE_URL = "https://app.censys.io/api/v1"


class MockResponse:
    # Dummy resource list to iterate over for testing paging
    RESOURCES = ["a", "b", "c"]
    # Dummy end of events list to simulate 3 pages of results
    END_OF_EVENTS = [False, False, True]

    def __init__(self, status_code, resource_type, page_number=1):
        self.number_generator = self.get_page_number()
        self.end_of_events_generator = self.get_end_of_events()
        self.resource_type = resource_type
        self.page_number = page_number
        self.status_code = status_code

        self.json_data = {
            resource_type: self.get_resource(),  # Return dummy resource generator
            "pageNumber": 1,
            "totalPages": 3,  # Default to 3 pages of resources
            "nextCursor": "eyJmaWx0ZXIiOnt9LCJzdGFydCI6MjA3MTJ9",
            "cursor": "eyJmaWx0ZXIiOnt9LCJzdGFydCI6MH0",
            "endOfEvents": False,
        }

    def json(self):
        self.json_data["endOfEvents"] = next(self.end_of_events_generator)
        self.json_data["pageNumber"] = next(self.number_generator)
        self.json_data[self.resource_type] = self.get_resource()

        return self.json_data

    # Generate dummy resources for pagination
    def get_resource(self):
        yield from self.RESOURCES

    # Generate next page number for pagination; max 10 pages
    def get_page_number(self):
        for i in range(0, 10):
            yield i + self.page_number

    # Generate endOfEvents boolean
    def get_end_of_events(self):
        yield from self.END_OF_EVENTS
