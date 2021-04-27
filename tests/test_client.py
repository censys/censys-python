from .utils import CensysTestCase

from censys import SearchClient

ALL_INDEXES = {
    "v1": ["certificates", "data", "ipv4", "websites"],
    "v2": ["hosts"],
}


class CensysSearchClientTest(CensysTestCase):
    def setUp(self):
        super().setUp()
        self.expected_auth = (self.api_id, self.api_secret)

    def test_api_creds_args(self):
        client = SearchClient(self.api_id, self.api_secret)
        for version, indexes in ALL_INDEXES.items():
            v = getattr(client, version)
            for index in indexes:
                assert getattr(v, index)._session.auth == self.expected_auth

    def test_api_creds_kwargs(self):
        client = SearchClient(api_id=self.api_id, api_secret=self.api_secret)
        for version, indexes in ALL_INDEXES.items():
            v = getattr(client, version)
            for index in indexes:
                assert getattr(v, index)._session.auth == self.expected_auth
