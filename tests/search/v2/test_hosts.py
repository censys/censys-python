import datetime
import json
from copy import deepcopy
from typing import Any, Dict, List, Optional

import pytest
import responses
from parameterized import parameterized
from responses import matchers

from tests.utils import V2_URL, CensysTestCase

from censys.common.exceptions import CensysInternalServerException
from censys.search import CensysHosts, SearchClient

TEST_HOST = "8.8.8.8"
TEST_SEARCH_QUERY = "services.service_name: HTTP"

VIEW_HOST_JSON = {
    "code": 200,
    "status": "OK",
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
    },
}

SEARCH_HOSTS_JSON = {
    "code": 200,
    "status": "OK",
    "result": {
        "query": "services.service_name: HTTP",
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

AGGREGATE_HOSTS_JSON = {
    "code": 200,
    "status": "OK",
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
        "query": "services.service_name: HTTP",
        "total": 149575980,
    },
}

VIEW_HOST_NAMES_JSON = {
    "code": 200,
    "status": "OK",
    "result": {"names": ["google.com", "google.co.uk", "google.com.au", "dns.google"]},
    "links": {"prev": "prevCursorToken", "next": "nextCursorToken"},
}

HOST_METADATA_JSON = {
    "code": 200,
    "status": "OK",
    "result": {"services": ["HTTP", "IMAP", "MQTT", "SSH", "..."]},
}

VIEW_HOST_DIFF_JSON = {
    "code": 200,
    "status": "OK",
    "result": {
        "a": {"ip": "1.1.1.1", "last_updated_at": "2022-01-10T15:41:27.416Z"},
        "b": {"ip": "1.1.1.2", "last_updated_at": "2022-01-10T15:41:27.416Z"},
        "patch": [{}],
    },
}

VIEW_HOST_EVENTS_JSON = {
    "code": 200,
    "status": "OK",
    "result": {
        "ip": "8.8.8.8",
        "events": [
            {
                "_event": "service_observed",
                "service_observed": {
                    "id": {
                        "port": 443,
                        "transport_protocol": "TCP",
                        "service_name": "HTTP",
                    },
                    "observed_at": "2021-07-27T18:00:11.296Z",
                    "perspective_id": "PERSPECTIVE_NTT",
                    "changed_fields": [{"field_name": "services.banner"}],
                },
                "timestamp": "2021-07-27T18:00:11.296Z",
            },
            {
                "_event": "location_updated",
                "location_updated": {
                    "location": {
                        "continent": "North America",
                        "country": "United States",
                        "country_code": "US",
                        "postal_code": "48104",
                        "timezone": "America/Michigan",
                        "coordinates": {"latitude": "42.273", "longitude": "-83.751"},
                        "registered_country": "United States",
                        "registered_country_code": "US",
                    }
                },
                "timestamp": "2021-07-27T18:00:11.297Z",
            },
        ],
    },
}
RATE_LIMIT_ERROR_JSON = {
    "error": "Rate limit exceeded. See https://search.censys.io/account "
    "for rate limit details.",
    "status": "error",
    "error_type": "rate_limit_exceeded",
}
TOO_MANY_REQUESTS_ERROR_JSON = {
    "code": 429,
    "status": "Too Many Requests",
    "error": "You have used your full quota for this billing period. Please see https://search.censys.io/account or contact support@censys.io.",
}
SERVER_ERROR_JSON = {
    "code": 500,
    "status": "Internal Server Error",
    "error": "An unexpected error occurred. Please try again later.",
}


class TestHosts(CensysTestCase):
    api: CensysHosts

    def setUp(self):
        super().setUp()
        self.setUpApi(SearchClient(self.api_id, self.api_secret).v2.hosts)

    def test_view(self):
        self.responses.add(
            responses.GET,
            f"{V2_URL}/hosts/{TEST_HOST}",
            status=200,
            json=VIEW_HOST_JSON,
        )

        res = self.api.view(TEST_HOST)

        assert res == VIEW_HOST_JSON["result"]

    def test_view_at_time(self):
        self.responses.add(
            responses.GET,
            f"{V2_URL}/hosts/{TEST_HOST}?at_time=2021-03-01T00:00:00.000000Z",  # noqa: E231
            status=200,
            json=VIEW_HOST_JSON,
        )

        date = datetime.date(2021, 3, 1)

        res = self.api.view(TEST_HOST, at_time=date)

        assert res == VIEW_HOST_JSON["result"]

    def test_bulk_view(self):
        ips = ["1.1.1.1", "1.1.1.2", "1.1.1.3"]
        expected = {}
        for ip in ips:
            host_json = deepcopy(VIEW_HOST_JSON)
            host_json["result"]["ip"] = ip
            self.responses.add(
                responses.GET,
                f"{V2_URL}/hosts/{ip}",
                status=200,
                json=host_json,
            )
            expected[ip] = deepcopy(host_json["result"])

        results = self.api.bulk_view(ips)
        assert results == expected

    def test_bulk_view_at_time(self):
        ips = ["1.1.1.1", "1.1.1.2", "1.1.1.3"]
        expected = {}
        for ip in ips:
            host_json = deepcopy(VIEW_HOST_JSON)
            host_json["result"]["ip"] = ip
            self.responses.add(
                responses.GET,
                f"{V2_URL}/hosts/{ip}?at_time=2021-03-01T00:00:00.000000Z",  # noqa: E231
                status=200,
                json=host_json,
            )
            expected[ip] = deepcopy(host_json["result"])

        date = datetime.date(2021, 3, 1)

        results = self.api.bulk_view(ips, at_time=date)
        assert results == expected

    def test_bulk_view_with_error(self):
        ips = ["1.1.1.1", "1.1.1.2", "1.1.1.3"]
        expected = {}
        for ip in ips[:-1]:
            host_json = deepcopy(VIEW_HOST_JSON)
            host_json["result"]["ip"] = ip
            self.responses.add(
                responses.GET,
                f"{V2_URL}/hosts/{ip}",
                status=200,
                json=host_json,
            )
            expected[ip] = deepcopy(host_json["result"])

        self.responses.add(
            responses.GET,
            f"{V2_URL}/hosts/{ips[-1]}",
            status=429,
            json=RATE_LIMIT_ERROR_JSON,
        )
        expected[ips[-1]] = {
            "error": "429 (rate_limit_exceeded): Rate limit exceeded. See https://search.censys.io/account for rate limit details."
        }

        results = self.api.bulk_view(ips)
        assert results == expected

    @parameterized.expand(
        [
            ("search_post_raw", True),
            ("raw_search", True),
            ("search_post"),
        ]
    )
    def test_search_post(self, method_name: str, raw: bool = False):
        self.responses.add(
            responses.POST,
            f"{V2_URL}/hosts/search",
            status=200,
            json=SEARCH_HOSTS_JSON,
            match=[
                matchers.json_params_matcher(
                    {
                        "q": TEST_SEARCH_QUERY,
                        "per_page": 100,
                    }
                )
            ],
        )
        method = getattr(self.api, method_name)
        result = method(TEST_SEARCH_QUERY)
        if raw:
            assert result == SEARCH_HOSTS_JSON
        else:
            assert result == SEARCH_HOSTS_JSON["result"]

    @parameterized.expand(
        [
            (None, None, None),
            (["ip", "services.port"], None, None),
            (None, "RELEVANCE", None),
            (
                ["ip", "services.port"],
                "RELEVANCE",
                None,
            ),
            (
                None,
                None,
                None,
                "ONLY",
            ),
            (None, None, "nextCursorToken"),
        ]
    )
    def test_search(
        self,
        fields: Optional[List[str]] = None,
        sort: Optional[str] = None,
        cursor: Optional[str] = None,
        virtual_hosts: Optional[str] = None,
    ):
        self.responses.add(
            responses.POST,
            f"{V2_URL}/hosts/search",
            status=200,
            json=SEARCH_HOSTS_JSON,
        )
        query = self.api.search(
            TEST_SEARCH_QUERY,
            fields=fields,
            sort=sort,
            cursor=cursor,
            virtual_hosts=virtual_hosts,
        )
        assert next(query) == SEARCH_HOSTS_JSON["result"]["hits"]

    def test_search_per_page(self):
        test_per_page = 50
        self.responses.add(
            responses.POST,
            V2_URL + "/hosts/search",
            status=200,
            json=SEARCH_HOSTS_JSON,
            match=[
                matchers.json_params_matcher(
                    {"q": "services.service_name: HTTP", "per_page": test_per_page}
                )
            ],
        )

        query = self.api.search("services.service_name: HTTP", per_page=test_per_page)
        assert next(query) == SEARCH_HOSTS_JSON["result"]["hits"]

    @parameterized.expand(
        [
            ({}, {"q": TEST_SEARCH_QUERY, "per_page": 100}),
            ({"per_page": 1}, {"q": TEST_SEARCH_QUERY, "per_page": 1}),
            (
                {"cursor": "nextCursorToken"},
                {"q": TEST_SEARCH_QUERY, "cursor": "nextCursorToken", "per_page": 100},
            ),
            (
                {"fields": ["ip"]},
                {"q": TEST_SEARCH_QUERY, "fields": "ip", "per_page": 100},
            ),
            (
                {
                    "fields": [
                        "ip",
                        "services.port",
                        "services.extended_service_name",
                    ]
                },
                {
                    "q": TEST_SEARCH_QUERY,
                    "fields": [
                        "ip",
                        "services.port",
                        "services.extended_service_name",
                    ],
                    "per_page": 100,
                },
            ),
            (
                {"sort": "RELEVANCE"},
                {
                    "q": TEST_SEARCH_QUERY,
                    "sort": "RELEVANCE",
                    "per_page": 100,
                },
            ),
        ]
    )
    def test_search_get(self, params: Dict[str, Any], expected_params: Dict[str, Any]):
        self.responses.add(
            responses.GET,
            f"{V2_URL}/hosts/search",
            status=200,
            json=SEARCH_HOSTS_JSON,
            match=[matchers.query_param_matcher(expected_params)],
        )
        result = self.api.search_get(TEST_SEARCH_QUERY, **params)
        assert result == SEARCH_HOSTS_JSON["result"]

    def test_search_with_error_retry(self):
        is_first_request = True

        def request_callback(_):
            nonlocal is_first_request
            if is_first_request:
                is_first_request = False
                return (429, {}, json.dumps(RATE_LIMIT_ERROR_JSON))
            return (200, {}, json.dumps(SEARCH_HOSTS_JSON))

        self.responses.add_callback(
            responses.POST,
            V2_URL + "/hosts/search",
            callback=request_callback,
            content_type="application/json",
        )

        query = self.api.search("services.service_name: HTTP")
        assert query() == SEARCH_HOSTS_JSON["result"]["hits"]

    def test_search_invalid_query(self):
        invalid_query = "some_bad_query"
        no_hosts_json = deepcopy(SEARCH_HOSTS_JSON)
        no_hosts_json["result"]["hits"] = []
        no_hosts_json["result"]["total"] = 0
        no_hosts_json["result"]["links"]["next"] = ""
        self.responses.add(
            responses.POST,
            V2_URL + "/hosts/search",
            status=200,
            json=no_hosts_json,
            match=[matchers.json_params_matcher({"q": invalid_query, "per_page": 100})],
        )

        query = self.api.search(invalid_query)
        assert next(query) == no_hosts_json["result"]["hits"]
        assert query.pages == 0
        with pytest.raises(StopIteration):
            next(query)

    def test_search_pages(self):
        self.responses.add(
            responses.POST,
            V2_URL + "/hosts/search",
            status=200,
            json=SEARCH_HOSTS_JSON,
            match=[
                matchers.json_params_matcher(
                    {"q": "services.service_name: HTTP", "per_page": 100}
                )
            ],
        )
        page_2_json = deepcopy(SEARCH_HOSTS_JSON)
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
        next_cursor = SEARCH_HOSTS_JSON["result"]["links"]["next"]
        page_2_json["result"]["hits"] = new_hits
        page_2_json["result"]["links"]["next"] = None
        self.responses.add(
            responses.POST,
            V2_URL + "/hosts/search",
            status=200,
            json=page_2_json,
            match=[
                matchers.json_params_matcher(
                    {
                        "q": "services.service_name: HTTP",
                        "per_page": 100,
                        "cursor": next_cursor,
                    }
                )
            ],
        )

        expected = [hits, new_hits]

        query = self.api.search("services.service_name: HTTP", pages=-1)
        for i, page in enumerate(query):
            assert expected[i] == page

    def test_search_pages_retry_with_server_error(self):
        first_request_to_second_page = True

        def request_callback(_):
            nonlocal first_request_to_second_page
            if first_request_to_second_page:
                first_request_to_second_page = False
                return (500, {}, json.dumps(SERVER_ERROR_JSON))
            return (200, {}, json.dumps(SEARCH_HOSTS_JSON))

        self.responses.add(
            responses.POST,
            V2_URL + "/hosts/search",
            status=200,
            json=SEARCH_HOSTS_JSON,
            match=[
                matchers.json_params_matcher(
                    {"q": "services.service_name: HTTP", "per_page": 100}
                )
            ],
        )
        self.responses.add_callback(
            responses.POST,
            V2_URL + "/hosts/search",
            callback=request_callback,
            content_type="application/json",
        )

        query = self.api.search("services.service_name: HTTP", pages=2)
        assert next(query) == SEARCH_HOSTS_JSON["result"]["hits"]
        assert next(query) == SEARCH_HOSTS_JSON["result"]["hits"], "Retry did not fail"

    def test_search_pages_retry_fail(self):
        self.responses.add(
            responses.POST,
            V2_URL + "/hosts/search",
            status=200,
            json=SEARCH_HOSTS_JSON,
            match=[
                matchers.json_params_matcher(
                    {"q": "services.service_name: HTTP", "per_page": 100}
                )
            ],
        )
        self.responses.add(
            responses.POST,
            V2_URL + "/hosts/search",
            status=500,
            json=SERVER_ERROR_JSON,
            match=[
                matchers.json_params_matcher(
                    {
                        "q": "services.service_name: HTTP",
                        "per_page": 100,
                        "cursor": "eyJBZnRlciI6WyIxIiwiMS4wLjAuNDkiXSwiUmV2ZXJzZSI6ZmFsc2V9",
                    }
                )
            ],
        )

        query = self.api.search("services.service_name: HTTP", pages=2)
        assert next(query) == SEARCH_HOSTS_JSON["result"]["hits"]
        with pytest.raises(CensysInternalServerException):
            next(query)

    def test_search_virtual_hosts(self):
        self.responses.add(
            responses.POST,
            V2_URL + "/hosts/search",
            status=200,
            json=SEARCH_HOSTS_JSON,
            match=[
                matchers.json_params_matcher(
                    {
                        "q": "services.service_name: HTTP",
                        "per_page": 100,
                        "virtual_hosts": "EXCLUDE",
                    }
                )
            ],
        )

        query = self.api.search("services.service_name: HTTP", virtual_hosts="EXCLUDE")
        assert query() == SEARCH_HOSTS_JSON["result"]["hits"]

    def test_search_fields(self):
        self.responses.add(
            responses.POST,
            V2_URL + "/hosts/search",
            status=200,
            json=SEARCH_HOSTS_JSON,
            match=[
                matchers.json_params_matcher(
                    {
                        "q": "services.service_name: HTTP",
                        "per_page": 100,
                        "fields": ["ip", "services.port"],
                    }
                )
            ],
        )

        query = self.api.search(
            "services.service_name: HTTP", fields=["ip", "services.port"]
        )
        assert query() == SEARCH_HOSTS_JSON["result"]["hits"]

    def test_aggregate(self):
        self.responses.add(
            responses.GET,
            V2_URL
            + "/hosts/aggregate?field=services.port&q=services.service_name: HTTP&num_buckets=4",
            status=200,
            json=AGGREGATE_HOSTS_JSON,
        )
        self.maxDiff = None
        res = self.api.aggregate(
            "services.service_name: HTTP", "services.port", num_buckets=4
        )

        assert res == AGGREGATE_HOSTS_JSON["result"]

    def test_aggregate_virtual_hosts(self):
        self.responses.add(
            responses.GET,
            V2_URL
            + "/hosts/aggregate?field=services.port&q=services.service_name: HTTP&num_buckets=5"
            + "&virtual_hosts=INCLUDE",
            status=200,
            json=AGGREGATE_HOSTS_JSON,
        )
        self.maxDiff = None
        res = self.api.aggregate(
            "services.service_name: HTTP",
            "services.port",
            num_buckets=5,
            virtual_hosts="INCLUDE",
        )

        assert res == AGGREGATE_HOSTS_JSON["result"]

    def test_search_view_all(self):
        test_per_page = 50
        ips = ["1.1.1.1", "1.1.1.2"]
        search_json = deepcopy(SEARCH_HOSTS_JSON)
        search_json["result"]["hits"] = [{"ip": ip} for ip in ips]
        search_json["result"]["total"] = len(ips)
        search_json["result"]["links"]["next"] = ""
        self.responses.add(
            responses.POST,
            f"{V2_URL}/hosts/search",
            status=200,
            json=search_json,
            match=[
                matchers.json_params_matcher(
                    {
                        "q": "services.service_name: HTTP",
                        "per_page": test_per_page,
                    }
                )
            ],
        )

        expected = {}
        for ip in ips:
            view_json = deepcopy(VIEW_HOST_JSON)
            view_json["result"]["ip"] = ip
            self.responses.add(
                responses.GET,
                f"{V2_URL}/hosts/{ip}",
                status=200,
                json=view_json,
            )
            expected[ip] = deepcopy(view_json["result"])

        query = self.api.search("services.service_name: HTTP", per_page=test_per_page)
        results = query.view_all()
        assert results == expected

    def test_search_view_all_virtual_hosts(self):
        test_per_page = 50
        search_json = deepcopy(SEARCH_HOSTS_JSON)
        hits = [{"ip": "1.1.1.1", "name": "one.one.one.one"}, {"ip": "1.0.0.1"}]
        search_json["result"]["hits"] = hits
        search_json["result"]["total"] = len(hits)
        search_json["result"]["links"]["next"] = ""
        self.responses.add(
            responses.POST,
            f"{V2_URL}/hosts/search",
            status=200,
            json=search_json,
            match=[
                matchers.json_params_matcher(
                    {
                        "q": "services.service_name: HTTP",
                        "per_page": test_per_page,
                    }
                )
            ],
        )

        expected = {}
        for hit in hits:
            view_json = deepcopy(VIEW_HOST_JSON)
            view_json["result"]["ip"] = hit["ip"]
            document_key = hit["ip"]
            if "name" in hit:
                document_key += "+" + hit["name"]
            self.responses.add(
                responses.GET,
                f"{V2_URL}/hosts/{document_key}",
                status=200,
                json=view_json,
            )
            expected[document_key] = deepcopy(view_json["result"])

        query = self.api.search("services.service_name: HTTP", per_page=test_per_page)
        results = query.view_all()
        assert results == expected

    def test_search_view_all_error(self):
        test_per_page = 50
        ips = ["1.1.1.1", "1.1.1.2", "1.1.1.3"]
        search_json = deepcopy(SEARCH_HOSTS_JSON)
        search_json["result"]["hits"] = [{"ip": ip} for ip in ips]
        search_json["result"]["total"] = len(ips)
        search_json["result"]["links"]["next"] = ""
        self.responses.add(
            responses.POST,
            f"{V2_URL}/hosts/search",
            status=200,
            json=search_json,
            match=[
                matchers.json_params_matcher(
                    {
                        "q": "services.service_name: HTTP",
                        "per_page": test_per_page,
                    }
                )
            ],
        )

        expected = {}
        for ip in ips[:-1]:
            view_json = deepcopy(VIEW_HOST_JSON)
            view_json["result"]["ip"] = ip
            self.responses.add(
                responses.GET,
                f"{V2_URL}/hosts/{ip}",
                status=200,
                json=view_json,
            )
            expected[ip] = deepcopy(view_json["result"])

        self.responses.add(
            responses.GET,
            f"{V2_URL}/hosts/{ips[-1]}",
            status=429,
            json=RATE_LIMIT_ERROR_JSON,
        )
        expected[ips[-1]] = {
            "error": "429 (rate_limit_exceeded): Rate limit exceeded. See https://search.censys.io/account for rate limit details."
        }

        query = self.api.search("services.service_name: HTTP", per_page=test_per_page)
        results = query.view_all()
        assert results == expected

    def test_view_host_names(self):
        self.responses.add(
            responses.GET,
            f"{V2_URL}/hosts/{TEST_HOST}/names",
            status=200,
            json=VIEW_HOST_NAMES_JSON,
        )
        results = self.api.view_host_names(TEST_HOST)
        assert results == VIEW_HOST_NAMES_JSON["result"]["names"]

    def test_view_host_names_pages(self):
        self.responses.add(
            responses.GET,
            f"{V2_URL}/hosts/{TEST_HOST}/names?per_page=50",
            status=200,
            json=VIEW_HOST_NAMES_JSON,
        )
        results = self.api.view_host_names(TEST_HOST, per_page=50)
        assert results == VIEW_HOST_NAMES_JSON["result"]["names"]

    def test_host_metadata(self):
        self.responses.add(
            responses.GET,
            f"{V2_URL}/metadata/hosts",
            status=200,
            json=HOST_METADATA_JSON,
        )
        results = self.api.metadata()
        assert results == HOST_METADATA_JSON["result"]

    def test_view_host_diff(self):
        self.responses.add(
            responses.GET,
            f"{V2_URL}/hosts/{TEST_HOST}/diff",
            status=200,
            json=VIEW_HOST_DIFF_JSON,
        )
        results = self.api.view_host_diff(TEST_HOST)
        assert results == VIEW_HOST_DIFF_JSON["result"]

    @parameterized.expand(
        [
            ({"ip_b": "1.1.1.2"}, "ip_b=1.1.1.2"),
            (
                {
                    "at_time": datetime.date(2021, 7, 1),
                    "at_time_b": datetime.date(2021, 7, 31),
                },
                "at_time=2021-07-01T00%3A00%3A00.000000Z&at_time_b=2021-07-31T00%3A00%3A00.000000Z",
            ),
        ]
    )
    def test_view_host_diff_params(self, kwargs: dict, query_params: str):
        self.responses.add(
            responses.GET,
            f"{V2_URL}/hosts/{TEST_HOST}/diff?{query_params}",
            status=200,
            json=VIEW_HOST_DIFF_JSON,
        )
        results = self.api.view_host_diff(TEST_HOST, **kwargs)
        assert results == VIEW_HOST_DIFF_JSON["result"]

    @parameterized.expand(
        [
            ({}, ""),
            ({"per_page": 50}, "per_page=50"),
            (
                {
                    "start_time": datetime.date(2021, 7, 1),
                    "end_time": datetime.date(2021, 7, 31),
                },
                "start_time=2021-07-01T00%3A00%3A00.000000Z&end_time=2021-07-31T00%3A00%3A00.000000Z",
            ),
            (
                {"cursor": "nextCursor", "reversed": True},
                "cursor=nextCursor&reversed=True",
            ),
        ]
    )
    def test_view_host_events_params(self, kwargs: dict, query_params: str):
        url = f"{V2_URL}/experimental/hosts/{TEST_HOST}/events"
        if query_params:
            url += "?" + query_params
        self.responses.add(
            responses.GET,
            url,
            status=200,
            json=VIEW_HOST_EVENTS_JSON,
        )
        results = self.api.view_host_events(TEST_HOST, **kwargs)
        assert results == VIEW_HOST_EVENTS_JSON["result"]

    @parameterized.expand(
        [
            ({}, {"per_page": 100}),
            ({"per_page": 50}, {"per_page": 50}),
            (
                {
                    "start_time": datetime.date(2021, 7, 1),
                },
                {"per_page": 100, "start_time": "2021-07-01T00:00:00.000000Z"},
            ),
            (
                {"cursor": "nextCursor"},
                {"per_page": 100, "cursor": "nextCursor"},
            ),
        ]
    )
    def test_view_host_certificates(self, kwargs: dict, query_params: dict):
        self.responses.add(
            responses.GET,
            f"{V2_URL}/hosts/{TEST_HOST}/certificates",
            status=200,
            json=VIEW_HOST_EVENTS_JSON,
            match=[matchers.query_param_matcher(query_params)],
        )
        results = self.api.view_host_certificates(TEST_HOST, **kwargs)
        assert results == VIEW_HOST_EVENTS_JSON["result"]
