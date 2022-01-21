import datetime

import pytest
import responses
from parameterized import parameterized

from tests.utils import V2_URL, CensysTestCase

from censys.search import CensysHosts, SearchClient

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
        "query": "service.service_name: HTTP",
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

TEST_HOST = "8.8.8.8"


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
            f"{V2_URL}/hosts/{TEST_HOST}?at_time=2021-03-01T00:00:00.000000Z",
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
            host_json = VIEW_HOST_JSON.copy()
            host_json["result"]["ip"] = ip
            self.responses.add(
                responses.GET,
                f"{V2_URL}/hosts/{ip}",
                status=200,
                json=host_json,
            )
            expected[ip] = host_json["result"].copy()

        results = self.api.bulk_view(ips)
        assert results == expected

    def test_bulk_view_at_time(self):
        ips = ["1.1.1.1", "1.1.1.2", "1.1.1.3"]
        expected = {}
        for ip in ips:
            host_json = VIEW_HOST_JSON.copy()
            host_json["result"]["ip"] = ip
            self.responses.add(
                responses.GET,
                f"{V2_URL}/hosts/{ip}?at_time=2021-03-01T00:00:00.000000Z",
                status=200,
                json=host_json,
            )
            expected[ip] = host_json["result"].copy()

        date = datetime.date(2021, 3, 1)

        results = self.api.bulk_view(ips, at_time=date)
        assert results == expected

    def test_bulk_view_with_error(self):
        ips = ["1.1.1.1", "1.1.1.2", "1.1.1.3"]
        expected = {}
        for ip in ips[:-1]:
            host_json = VIEW_HOST_JSON.copy()
            host_json["result"]["ip"] = ip
            self.responses.add(
                responses.GET,
                f"{V2_URL}/hosts/{ip}",
                status=200,
                json=host_json,
            )
            expected[ip] = host_json["result"].copy()

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

    def test_search(self):
        self.responses.add(
            responses.GET,
            V2_URL + "/hosts/search?q=service.service_name: HTTP&per_page=100",
            status=200,
            json=SEARCH_HOSTS_JSON,
        )

        query = self.api.search("service.service_name: HTTP")
        assert query() == SEARCH_HOSTS_JSON["result"]["hits"]

    def test_search_per_page(self):
        test_per_page = 50
        self.responses.add(
            responses.GET,
            V2_URL
            + f"/hosts/search?q=service.service_name: HTTP&per_page={test_per_page}",
            status=200,
            json=SEARCH_HOSTS_JSON,
        )

        query = self.api.search("service.service_name: HTTP", per_page=test_per_page)
        assert next(query) == SEARCH_HOSTS_JSON["result"]["hits"]

    def test_search_invalid_query(self):
        invalid_query = "some_bad_query"
        no_hosts_json = SEARCH_HOSTS_JSON.copy()
        no_hosts_json["result"]["hits"] = []
        no_hosts_json["result"]["total"] = 0
        no_hosts_json["result"]["links"]["next"] = ""
        self.responses.add(
            responses.GET,
            V2_URL + f"/hosts/search?q={invalid_query}&per_page=100",
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
            V2_URL + "/hosts/search?q=service.service_name%3A+HTTP&per_page=100",
            status=200,
            json=SEARCH_HOSTS_JSON,
        )
        page_2_json = SEARCH_HOSTS_JSON.copy()
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
            responses.GET,
            V2_URL
            + "/hosts/search?q=service.service_name%3A+HTTP&per_page=100"
            + f"&cursor={next_cursor}",
            status=200,
            json=page_2_json,
        )

        expected = [hits, new_hits]

        query = self.api.search("service.service_name: HTTP", pages=-1)
        for i, page in enumerate(query):
            assert expected[i] == page

    def test_search_virtual_hosts(self):
        self.responses.add(
            responses.GET,
            V2_URL
            + "/hosts/search?q=service.service_name%3A+HTTP&per_page=100&virtual_hosts=EXCLUDE",
            status=200,
            json=SEARCH_HOSTS_JSON,
        )

        query = self.api.search("service.service_name: HTTP", virtual_hosts="EXCLUDE")
        assert query() == SEARCH_HOSTS_JSON["result"]["hits"]

    def test_aggregate(self):
        self.responses.add(
            responses.GET,
            V2_URL
            + "/hosts/aggregate?field=services.port&q=service.service_name: HTTP&num_buckets=4",
            status=200,
            json=AGGREGATE_HOSTS_JSON,
        )
        self.maxDiff = None
        res = self.api.aggregate(
            "service.service_name: HTTP", "services.port", num_buckets=4
        )

        assert res == AGGREGATE_HOSTS_JSON["result"]

    def test_aggregate_virtual_hosts(self):
        self.responses.add(
            responses.GET,
            V2_URL
            + "/hosts/aggregate?field=services.port&q=service.service_name: HTTP&num_buckets=5"
            + "&virtual_hosts=INCLUDE",
            status=200,
            json=AGGREGATE_HOSTS_JSON,
        )
        self.maxDiff = None
        res = self.api.aggregate(
            "service.service_name: HTTP",
            "services.port",
            num_buckets=5,
            virtual_hosts="INCLUDE",
        )

        assert res == AGGREGATE_HOSTS_JSON["result"]

    def test_search_view_all(self):
        test_per_page = 50
        ips = ["1.1.1.1", "1.1.1.2"]
        search_json = SEARCH_HOSTS_JSON.copy()
        search_json["result"]["hits"] = [{"ip": ip} for ip in ips]
        search_json["result"]["total"] = len(ips)
        search_json["result"]["links"]["next"] = ""
        self.responses.add(
            responses.GET,
            f"{V2_URL}/hosts/search?q=service.service_name: HTTP&per_page={test_per_page}",
            status=200,
            json=search_json,
        )

        expected = {}
        for ip in ips:
            view_json = VIEW_HOST_JSON.copy()
            view_json["result"]["ip"] = ip
            self.responses.add(
                responses.GET,
                f"{V2_URL}/hosts/{ip}",
                status=200,
                json=view_json,
            )
            expected[ip] = view_json["result"].copy()

        query = self.api.search("service.service_name: HTTP", per_page=test_per_page)
        results = query.view_all()
        assert results == expected

    def test_search_view_all_error(self):
        test_per_page = 50
        ips = ["1.1.1.1", "1.1.1.2", "1.1.1.3"]
        search_json = SEARCH_HOSTS_JSON.copy()
        search_json["result"]["hits"] = [{"ip": ip} for ip in ips]
        search_json["result"]["total"] = len(ips)
        search_json["result"]["links"]["next"] = ""
        self.responses.add(
            responses.GET,
            f"{V2_URL}/hosts/search?q=service.service_name: HTTP&per_page={test_per_page}",
            status=200,
            json=search_json,
        )

        expected = {}
        for ip in ips[:-1]:
            view_json = VIEW_HOST_JSON.copy()
            view_json["result"]["ip"] = ip
            self.responses.add(
                responses.GET,
                f"{V2_URL}/hosts/{ip}",
                status=200,
                json=view_json,
            )
            expected[ip] = view_json["result"].copy()

        self.responses.add(
            responses.GET,
            f"{V2_URL}/hosts/{ips[-1]}",
            status=429,
            json=RATE_LIMIT_ERROR_JSON,
        )
        expected[ips[-1]] = {
            "error": "429 (rate_limit_exceeded): Rate limit exceeded. See https://search.censys.io/account for rate limit details."
        }

        query = self.api.search("service.service_name: HTTP", per_page=test_per_page)
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
    def test_view_host_diff_params(self, kwargs, query_params):
        self.responses.add(
            responses.GET,
            f"{V2_URL}/hosts/{TEST_HOST}/diff?{query_params}",
            status=200,
            json=VIEW_HOST_DIFF_JSON,
        )
        results = self.api.view_host_diff(TEST_HOST, **kwargs)
        assert results == VIEW_HOST_DIFF_JSON["result"]

    def test_view_host_events(self):
        self.responses.add(
            responses.GET,
            f"{V2_URL}/experimental/hosts/{TEST_HOST}/events",
            status=200,
            json=VIEW_HOST_EVENTS_JSON,
        )
        results = self.api.view_host_events(TEST_HOST)
        assert results == VIEW_HOST_EVENTS_JSON["result"]["events"]

    @parameterized.expand(
        [
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
    def test_view_host_events_params(self, kwargs, query_params):
        self.responses.add(
            responses.GET,
            f"{V2_URL}/experimental/hosts/{TEST_HOST}/events?{query_params}",
            status=200,
            json=VIEW_HOST_EVENTS_JSON,
        )
        results = self.api.view_host_events(TEST_HOST, **kwargs)
        assert results == VIEW_HOST_EVENTS_JSON["result"]["events"]
