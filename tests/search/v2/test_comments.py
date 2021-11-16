from typing import Type

import responses
from parameterized import parameterized_class

from tests.utils import CensysTestCase

from censys.search.v2 import CensysCerts, CensysHosts
from censys.search.v2.api import CensysSearchAPIv2

TEST_COMMENT = "**This is a comment.**"
GET_COMMENTS_RESPONSE = {
    "code": 200,
    "status": "OK",
    "result": {
        "ip": "8.8.8.8",
        "comments": [
            {
                "id": "comment-id",
                "ip": "1.1.1.1",
                "author_id": "string",
                "contents": TEST_COMMENT,
                "created_at": "2016-01-01T00:00:00Z",
            }
        ],
    },
}
ADD_COMMENTS_RESPONSE = {
    "code": 200,
    "status": "OK",
    "result": {
        "id": "comment-id",
        "ip": "1.1.1.1",
        "author_id": "string",
        "contents": TEST_COMMENT,
        "created_at": "2016-01-01T00:00:00Z",
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
class CensysCommentsTests(CensysTestCase):
    index: str
    index_cls: Type[CensysSearchAPIv2]
    document_id: str
    api: Type[CensysSearchAPIv2]

    def setUp(self):
        super().setUp()
        self.setUpApi(self.index_cls(self.api_id, self.api_secret))

    def test_get_comments(self):
        self.responses.add(
            responses.GET,
            f"{self.base_url}/{self.index}/{self.document_id}/comments",
            status=200,
            json=GET_COMMENTS_RESPONSE,
        )
        results = self.api.get_comments(self.document_id)
        assert results == GET_COMMENTS_RESPONSE["result"]["comments"]

    def test_add_comment(self):
        self.responses.add(
            responses.POST,
            f"{self.base_url}/{self.index}/{self.document_id}/comments",
            status=200,
            json=ADD_COMMENTS_RESPONSE,
            match=[responses.json_params_matcher({"contents": TEST_COMMENT})],
        )
        results = self.api.add_comment(self.document_id, TEST_COMMENT)
        assert results == ADD_COMMENTS_RESPONSE["result"]

    def test_delete_comment(self):
        self.responses.add(
            responses.DELETE,
            f"{self.base_url}/{self.index}/{self.document_id}/comments/comment-id",
            status=209,
        )
        self.api.delete_comment(self.document_id, "comment-id")

    def test_update_comment(self):
        self.responses.add(
            responses.PUT,
            f"{self.base_url}/{self.index}/{self.document_id}/comments/comment-id",
            status=200,
            json={"code": 200, "status": "OK"},
            match=[responses.json_params_matcher({"contents": TEST_COMMENT})],
        )
        results = self.api.update_comment(self.document_id, "comment-id", TEST_COMMENT)
        assert results == {"code": 200, "status": "OK"}
