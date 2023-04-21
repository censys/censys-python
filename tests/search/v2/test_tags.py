import pytest
import responses
from parameterized import parameterized_class

from tests.utils import BASE_URL, CensysTestCase

from censys.search.v2 import CensysCerts, CensysHosts
from censys.search.v2.api import CensysSearchAPIv2

TEST_TAG_NAME = "is-honeypot"
TEST_TAG_COLOR = "#ff0000"
TEST_TAG_ID = "123"
LIST_TAGS_RESPONSE = {
    "code": 200,
    "status": "OK",
    "result": {
        "tags": [
            {
                "id": TEST_TAG_ID,
                "name": TEST_TAG_NAME,
                "metadata": {"color": TEST_TAG_COLOR},
                "created_at": "2021-01-01T00:00:00.000000Z",
                "updated_at": "2021-02-01T00:00:00.000000Z",
            }
        ]
    },
}
CREATE_TAG_RESPONSE = {
    "code": 200,
    "status": "OK",
    "result": {
        "id": TEST_TAG_ID,
        "name": TEST_TAG_NAME,
        "metadata": {"color": TEST_TAG_COLOR},
        "created_at": "2021-01-01T00:00:00.000000Z",
        "updated_at": "2021-02-01T00:00:00.000000Z",
    },
}
LIST_HOSTS_RESPONSE = {
    "code": 200,
    "status": "OK",
    "result": {
        "hosts": [{"ip": "1.1.1.1", "tagged_at": "2021-01-01T12:00:00.000000Z"}]
    },
}
LIST_CERTS_RESPONSE = {
    "code": 200,
    "status": "OK",
    "result": {
        "certs": [
            {
                "fingerprint": "e58e89a726d80bb0219b218c3ab9d818b4be75d77959508400d660ebe1c1be3d",
                "tagged_at": "2021-01-01T12:00:00.000000Z",
            }
        ]
    },
}


@parameterized_class(
    [
        {"index": "hosts", "index_cls": CensysHosts, "document_id": "1.0.0.0"},
        {
            "index": "certificates",
            "index_cls": CensysCerts,
            "document_id": "fb444eb8e68437bae06232b9f5091bccff62a768ca09e92eb5c9c2cf9d17c426",
        },
    ]
)
class CensysTagsTests(CensysTestCase):
    index: str
    index_cls: CensysSearchAPIv2
    document_id: str
    api: CensysSearchAPIv2

    def setUp(self):
        super().setUp()
        self.setUpApi(self.index_cls(self.api_id, self.api_secret))

    def test_list_all_tags(self):
        self.responses.add(
            responses.GET,
            BASE_URL + self.api.tags_path,
            status=200,
            json=LIST_TAGS_RESPONSE,
        )
        results = self.api.list_all_tags()
        assert results == LIST_TAGS_RESPONSE["result"]["tags"]

    def test_create_tag(self):
        self.responses.add(
            responses.POST,
            BASE_URL + self.api.tags_path,
            status=200,
            json=CREATE_TAG_RESPONSE,
            match=[
                responses.json_params_matcher(
                    {"name": TEST_TAG_NAME, "metadata": {"color": TEST_TAG_COLOR}}
                )
            ],
        )
        results = self.api.create_tag(TEST_TAG_NAME, TEST_TAG_COLOR)
        assert results == CREATE_TAG_RESPONSE["result"]

    def test_get_tag(self):
        self.responses.add(
            responses.GET,
            BASE_URL + self.api.tags_path + "/" + TEST_TAG_ID,
            status=200,
            json=CREATE_TAG_RESPONSE,
        )
        results = self.api.get_tag(TEST_TAG_ID)
        assert results == CREATE_TAG_RESPONSE["result"]

    def test_update_tag(self):
        self.responses.add(
            responses.PUT,
            BASE_URL + self.api.tags_path + "/" + TEST_TAG_ID,
            status=200,
            json=CREATE_TAG_RESPONSE,
            match=[
                responses.json_params_matcher(
                    {"name": TEST_TAG_NAME, "metadata": {"color": TEST_TAG_COLOR}}
                )
            ],
        )
        results = self.api.update_tag(TEST_TAG_ID, TEST_TAG_NAME, TEST_TAG_COLOR)
        assert results == CREATE_TAG_RESPONSE["result"]

    def test_delete_tag(self):
        self.responses.add(
            responses.DELETE,
            BASE_URL + self.api.tags_path + "/" + TEST_TAG_ID,
            status=204,
        )
        self.api.delete_tag(TEST_TAG_ID)
        assert len(self.responses.calls) == 1

    def test_list_tags_on_document(self):
        self.responses.add(
            responses.GET,
            BASE_URL + self.api.view_path + self.document_id + "/tags",
            status=200,
            json=LIST_TAGS_RESPONSE,
        )
        results = self.api.list_tags_on_document(self.document_id)
        assert results == LIST_TAGS_RESPONSE["result"]["tags"]

    def test_add_tag_to_document(self):
        self.responses.add(
            responses.PUT,
            f"{BASE_URL}{self.api.view_path}{self.document_id}/tags/{TEST_TAG_ID}",
            status=200,
        )
        self.api.add_tag_to_document(self.document_id, TEST_TAG_ID)
        assert len(self.responses.calls) == 1

    def test_remove_tag_to_document(self):
        self.responses.add(
            responses.DELETE,
            f"{BASE_URL}{self.api.view_path}{self.document_id}/tags/{TEST_TAG_ID}",
            status=200,
        )
        self.api.remove_tag_from_document(self.document_id, TEST_TAG_ID)
        assert len(self.responses.calls) == 1

    def test_list_hosts_with_tag(self):
        if self.index == "certificates":
            pytest.skip("Only applicable to hosts assets")
        self.responses.add(
            responses.GET,
            BASE_URL + self.api.tags_path + "/" + TEST_TAG_ID + "/hosts",
            status=200,
            json=LIST_HOSTS_RESPONSE,
        )
        results = self.api.list_hosts_with_tag(TEST_TAG_ID)
        assert results == [
            host["ip"] for host in LIST_HOSTS_RESPONSE["result"]["hosts"]
        ]

    def test_list_certs_with_tag(self):
        if self.index == "hosts":
            pytest.skip("Only applicable to certs assets")
        self.responses.add(
            responses.GET,
            BASE_URL + self.api.tags_path + "/" + TEST_TAG_ID + "/certificates",
            status=200,
            json=LIST_CERTS_RESPONSE,
        )
        results = self.api.list_certs_with_tag(TEST_TAG_ID)
        assert results == LIST_CERTS_RESPONSE["result"]["certs"]
