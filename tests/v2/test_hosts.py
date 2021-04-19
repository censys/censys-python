import datetime

import pytest
import responses

from ..utils import CensysTestCase

from censys import SearchClient

VIEW_HOST_JSON = {
    "result": {
        "services": [
            {
                "transport_protocol": "UDP",
                "truncated": False,
                "service_name": "DNS",
                "_decoded": "dns",
                "source_ip": "167.248.133.40",
                "extended_service_name": "DNS",
                "observed_at": "2021-04-01T13:40:03.755876935Z",
                "dns": {"server_type": "FORWARDING"},
                "perspective_id": "PERSPECTIVE_NTT",
                "port": 53,
                "software": [],
            }
        ],
        "ip": "8.8.8.8",
        "location_updated_at": "2021-03-30T14:53:12.980328Z",
        "location": {
            "country": "United States",
            "coordinates": {"latitude": 37.751, "longitude": -97.822},
            "registered_country": "United States",
            "registered_country_code": "US",
            "postal_code": "",
            "country_code": "US",
            "timezone": "America/Chicago",
            "continent": "North America",
        },
        "last_updated_at": "2021-04-01T14:10:10.712Z",
    }
}

HTTP_SEARCH_JSON = {
    "result": {
        "query": "service.service_name: HTTP",
        "hits": [
            {
                "services": [
                    {"service_name": "HTTP", "port": 443},
                    {"service_name": "HTTP", "port": 80},
                ],
                "ip": "1.0.0.0",
            },
            {
                "services": [
                    {"service_name": "HTTP", "port": 443},
                    {"service_name": "HTTP", "port": 80},
                ],
                "ip": "1.0.0.1",
            },
        ],
        "total": 146857082,
        "links": {
            "prev": "eyJBZnRlciI6WyIxIiwiMS4wLjAuMCJdLCJSZXZlcnNlIjp0cnVlfQ==",
            "next": "eyJBZnRlciI6WyIxIiwiMS4wLjAuNDkiXSwiUmV2ZXJzZSI6ZmFsc2V9",
        },
    },
}

HTTP_AGGREGATE_JSON = {
    "result": {
        "total_omitted": 358388380,
        "buckets": [
            {"count": 47637476, "key": "80"},
            {"count": 35073802, "key": "443"},
            {"count": 17256198, "key": "7547"},
            {"count": 13216884, "key": "22"},
        ],
        "potential_deviation": 605118,
        "field": "services.port",
        "query": "service.service_name: HTTP",
        "total": 149575980,
    }
}


class TestHosts(CensysTestCase):
    def setUp(self):
        super().setUp()
        self.setUpApi(SearchClient(self.api_id, self.api_secret).v2.hosts)

    def test_view(self):
        self.responses.add(
            responses.GET,
            self.base_url + "/hosts/8.8.8.8",
            status=200,
            json=VIEW_HOST_JSON,
        )

        res = self.api.view("8.8.8.8")

        assert res == VIEW_HOST_JSON["result"]

    def test_view_at_time(self):
        self.responses.add(
            responses.GET,
            self.base_url + "/hosts/8.8.8.8?at_time=2021-03-01T00:00:00.000000Z",
            status=200,
            json=VIEW_HOST_JSON,
        )

        date = datetime.date(2021, 3, 1)

        res = self.api.view("8.8.8.8", at_time=date)

        assert res == VIEW_HOST_JSON["result"]

    def test_search(self):
        self.responses.add(
            responses.GET,
            self.base_url + "/hosts/search?q=service.service_name: HTTP&per_page=100",
            status=200,
            json=HTTP_SEARCH_JSON,
        )

        query = self.api.search("service.service_name: HTTP")
        assert query() == HTTP_SEARCH_JSON["result"]["hits"]

    def test_search_per_page(self):
        test_per_page = 50
        self.responses.add(
            responses.GET,
            self.base_url
            + f"/hosts/search?q=service.service_name: HTTP&per_page={test_per_page}",
            status=200,
            json=HTTP_SEARCH_JSON,
        )

        query = self.api.search("service.service_name: HTTP", per_page=test_per_page)
        assert next(query) == HTTP_SEARCH_JSON["result"]["hits"]

    def test_search_invalid_query(self):
        invalid_query = "some_bad_query"
        no_hosts_json = HTTP_SEARCH_JSON.copy()
        no_hosts_json["result"]["hits"] = []
        no_hosts_json["result"]["total"] = 0
        no_hosts_json["result"]["links"]["next"] = ""
        self.responses.add(
            responses.GET,
            self.base_url + f"/hosts/search?q={invalid_query}&per_page=100",
            status=200,
            json=no_hosts_json,
        )

        query = self.api.search(invalid_query)
        assert next(query) == no_hosts_json["result"]["hits"]
        assert query.pages == 0
        with pytest.raises(StopIteration):
            next(query)

    def test_search_pages(self):
        self.responses.add(
            responses.GET,
            self.base_url + "/hosts/search?q=service.service_name: HTTP&per_page=100",
            status=200,
            json=HTTP_SEARCH_JSON,
        )
        page_2_json = HTTP_SEARCH_JSON.copy()
        hits = page_2_json["result"]["hits"]
        new_hits = [
            {
                "services": [
                    {"service_name": "HTTP", "port": 443},
                    {"service_name": "HTTP", "port": 80},
                ],
                "ip": "1.0.0.2",
            }
        ]
        next_cursor = HTTP_SEARCH_JSON["result"]["links"]["next"]
        page_2_json["result"]["hits"] = new_hits
        self.responses.add(
            responses.GET,
            self.base_url
            + "/hosts/search?q=service.service_name: HTTP&per_page=100"
            + f"&cursor={next_cursor}",
            status=200,
            json=page_2_json,
        )

        expected = [hits, new_hits]

        query = self.api.search("service.service_name: HTTP", pages=2)
        for i, page in enumerate(query):
            assert expected[i] == page

    def test_aggregate(self):
        self.responses.add(
            responses.GET,
            self.base_url
            + "/hosts/aggregate?field=services.port&q=service.service_name: HTTP&num_buckets=4",
            status=200,
            json=HTTP_AGGREGATE_JSON,
        )
        self.maxDiff = None
        res = self.api.aggregate(
            "service.service_name: HTTP", "services.port", num_buckets=4
        )

        assert res == HTTP_AGGREGATE_JSON["result"]
