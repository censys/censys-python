import os
import unittest
import pytest

from censys.config import DEFAULT, get_config

config = get_config()
api_key = config.get(DEFAULT, "api_key") or os.getenv("CENSYS_API_KEY")

required_env_asm = pytest.mark.skipif(
    not api_key, reason="API key not found",
)

RESOURCE_PAGING_RESULTS = ['a', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'c']
TEST_TIMEOUT = 30
TEST_SUCCESS_CODE = 200
BASE_URL = 'https://app.censys.io/api/v1'


@required_env_asm
class CensysAsmTestCase(unittest.TestCase):
    pass


class MockResponse:
    # Dummy resource list to iterate over for testing paging
    RESOURCES = ['a', 'b', 'c']
    # Dummy end of events list to simulate 3 pages of results
    END_OF_EVENTS = [False, False, True]

    def __init__(self, status_code, resource_type, page_number=1):
        self.number_generator = self.get_page_number()
        self.end_of_events_generator = self.get_end_of_events()
        self.resource_type = resource_type
        self.page_number = page_number
        self.status_code = status_code

        self.json_data = {
            resource_type: self.get_resource(),  # Return a unique dummy resource generator
            'pageNumber': 1,
            'totalPages': 3,  # Default to 3 pages of resources
            'cursor': 'eyJmaWx0ZXIiOnt9LCJzdGFydCI6MjA3MTJ9',
            'endOfEvents': False
        }

    def json(self):
        self.json_data['endOfEvents'] = next(self.end_of_events_generator)
        self.json_data['pageNumber'] = next(self.number_generator)
        self.json_data[self.resource_type] = self.get_resource()

        return self.json_data

    # Generate dummy resources for pagination
    def get_resource(self):
        for resource in self.RESOURCES:
            yield resource

    # Generate next page number for pagination; max 10 pages
    def get_page_number(self):
        for i in range(0, 10):
            yield i + self.page_number

    # Generate endOfEvents boolean
    def get_end_of_events(self):
        for eov in self.END_OF_EVENTS:
            yield eov
