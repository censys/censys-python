from typing import Any, Dict

import responses
from parameterized import parameterized
from responses import matchers

from tests.utils import V2_URL, CensysTestCase

from censys.search import SearchClient

TEST_CERT = "fb444eb8e68437bae06232b9f5091bccff62a768ca09e92eb5c9c2cf9d17c426"
ALTERNATE_CERT = "9b00121b4e85d50667ded1a8aa39855771bdb67ceca6f18726b49374b41f0041"
TEST_SEARCH_QUERY = "parsed.subject.country: AU"
TEST_AGGREGATION_FIELD = "parsed.issuer.organization"

EXAMPLE_CERT_JSON = {
    "fingerprint_sha256": "9b00121b4e85d50667ded1a8aa39855771bdb67ceca6f18726b49374b41f0041",
    "fingerprint_sha1": "d508e7f8163fb67434f84091dc7c2ca8afd5234d",
    "fingerprint_md5": "3818d99263b47ab28f7de5b293ee1418",
    "tbs_fingerprint_sha256": "4b098b6bd9459340fb0f3cfb80f0bc3283370c455d57ca20da40e7eecce341d5",
    "tbs_no_ct_fingerprint_sha256": "5c095a40e76c245323086d26d1fa428d3b443b42fb58c7dbb19b32dfe516b749",
    "spki_fingerprint_sha256": "cc9b074ebf41b484a56923d5585594967bda7a7f8b5be187ef0e7ae1ec90003c",
    "parent_spki_fingerprint_sha256": "390bc358202771a65e7be7a87924d7f2a079de04feb5ffd4163fae4fbf9b11e9",
    "parsed": {
        "version": 3,
        "serial_number": "311703586789118042424998420179537559397550",
        "issuer_dn": "C=US, O=Let's Encrypt, CN=R3",
        "issuer": {
            "common_name": ["R3"],
            "country": ["US"],
            "organization": ["Let's Encrypt"],
        },
        "subject_dn": "CN=www.kgcontracting.co",
        "subject": {"common_name": ["www.kgcontracting.co"]},
        "subject_key_info": {
            "key_algorithm": {"name": "RSA", "oid": "1.2.840.113549.1.1.1"},
            "rsa": {
                "exponent": 65537,
                "_encoding": {"modulus": "DISPLAY_HEX"},
                "modulus": "c0b3b7d595e250fcbc54c6f9e81113c12da29fe35350a02b8ab769a5e43f07df7ac8ff72c482b3e838d64e97cb3fa15e415acbcfe6758a4e7ac401b4a5294ecca6ad1b583ec2136a408524eeadca55ba4a8af490cb9c764efbdecbe59a4ca160905e5972548018f55194e7ac94b2153d97bd5f055d58ad3abe0d1daa3b3c97fed490f1bb58fc5c819618891d05c32d68aeaabada321736e417f0fa58d7093d352c1800191645d1b820f5f7c93301ab7ca78393e953b82719741b735a67ce6a63faec0ac9d2d917f03b9fc0a0ab8012f4763c50118663af897294e85ba6e11c5ca0fd749645c2a58ddf14ad62717b40b5e7b620d256be28789e1ebd62e8046acd",
                "length": 2048,
            },
            "_encoding": {"fingerprint_sha256": "DISPLAY_HEX"},
            "fingerprint_sha256": "754cb1e2e2088214a5970662bb5a60aec8a2e29b94f53529aa608abee6682c60",
            "_key": "rsa",
        },
        "validity_period": {
            "not_before": "2022-12-31T11:37:55Z",
            "not_after": "2023-03-31T11:37:54Z",
            "length_seconds": 7775999,
        },
        "signature": {
            "signature_algorithm": {
                "name": "SHA256-RSA",
                "oid": "1.2.840.113549.1.1.11",
            },
            "_encoding": {"value": "DISPLAY_HEX"},
            "value": "95347a7bd89da6a6bd9adcc509669d933b5e2a29b414317d72b02c583bfadbf616f5b6977824ee80484fe4ae0c38dbb1013d896b5a9db12fdc62296fbefbba84ed089a6e62c148cc9d1e60bfd9cf6e7d1c8f5e0f315872618a6805e5bf48432ce2d0aac07d4ab845a7f68c1a61c3dd37c0e40c26b386b1f37ff2fc50e6eacdc305ecd13da1c43bb1209cb13c5a6387cffb57fad81d01496b3c6499817ed1cf1a0ef809b6b408035b5de72423c6c7f84c3a9e9513c89fa8fc49bf6f90746561ebd1b4ea22e7557d3e505b5ecd289dbb8ce71c4d3acc2e67a27bbb12dd242c8fa512d19dc8b7bd6b88bcc6a6484bb39c894f7b756630a10525a9ab3359030aa2ad",
            "valid": True,
            "self_signed": False,
        },
        # Removed extensions for brevity
        "serial_number_hex": "039403b7283199171fd9c1af1c8210f5a4ae",
        "redacted": False,
    },
    "names": ["kgcontracting.co", "www.kgcontracting.co"],
    "validation_level": "DV",
    "validation": {
        "nss": {
            "ever_valid": True,
            "had_trusted_path": True,
            "chains": [
                {
                    "_encoding": {"sha256fp": "DISPLAY_HEX"},
                    "sha256fp": [
                        "0ac730f6b3a98bab6aa97c9c4c71b34dd5599f4933630e6d24a26751bd12ebac",
                        "96bcec06264976f37460779acf28c5a7cfe8a3c0aae11a8ffcee05c0bddf08c6",
                    ],
                },
                {
                    "_encoding": {"sha256fp": "DISPLAY_HEX"},
                    "sha256fp": [
                        "67add1166b020ae61b8f5fc96813c04c2aa589960796865572a3c7e737613dfd",
                        "96bcec06264976f37460779acf28c5a7cfe8a3c0aae11a8ffcee05c0bddf08c6",
                    ],
                },
            ],
            "_encoding": {"parents": "DISPLAY_HEX"},
            "parents": [
                "0ac730f6b3a98bab6aa97c9c4c71b34dd5599f4933630e6d24a26751bd12ebac",
                "67add1166b020ae61b8f5fc96813c04c2aa589960796865572a3c7e737613dfd",
            ],
            "type": "LEAF",
            "is_valid": False,
            "has_trusted_path": False,
            "in_revocation_set": False,
        },
        # Removed additional validation data for brevity
    },
    "ever_seen_in_scan": True,
    "raw": "MIIFPzCCBCegAwIBAgISA5QDtygxmRcf2cGvHIIQ9aSuMA0GCSqGSIb3DQEBCwUAMDIxCzAJBgNVBAYTAlVTMRYwFAYDVQQKEw1MZXQncyBFbmNyeXB0MQswCQYDVQQDEwJSMzAeFw0yMjEyMzExMTM3NTVaFw0yMzAzMzExMTM3NTRaMB8xHTAbBgNVBAMTFHd3dy5rZ2NvbnRyYWN0aW5nLmNvMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwLO31ZXiUPy8VMb56BETwS2in+NTUKArirdppeQ/B996yP9yxIKz6DjWTpfLP6FeQVrLz+Z1ik56xAG0pSlOzKatG1g+whNqQIUk7q3KVbpKivSQy5x2Tvvey+WaTKFgkF5ZclSAGPVRlOeslLIVPZe9XwVdWK06vg0dqjs8l/7UkPG7WPxcgZYYiR0Fwy1orqq62jIXNuQX8PpY1wk9NSwYABkWRdG4IPX3yTMBq3yng5PpU7gnGXQbc1pnzmpj+uwKydLZF/A7n8Cgq4AS9HY8UBGGY6+JcpToW6bhHFyg/XSWRcKljd8UrWJxe0C157Yg0la+KHieHr1i6ARqzQIDAQABo4ICYDCCAlwwDgYDVR0PAQH/BAQDAgWgMB0GA1UdJQQWMBQGCCsGAQUFBwMBBggrBgEFBQcDAjAMBgNVHRMBAf8EAjAAMB0GA1UdDgQWBBSmobmsnQiGs7WPX6up9C90HZ7ynTAfBgNVHSMEGDAWgBQULrMXt1hWy65QCUDmH6+dixTCxjBVBggrBgEFBQcBAQRJMEcwIQYIKwYBBQUHMAGGFWh0dHA6Ly9yMy5vLmxlbmNyLm9yZzAiBggrBgEFBQcwAoYWaHR0cDovL3IzLmkubGVuY3Iub3JnLzAxBgNVHREEKjAoghBrZ2NvbnRyYWN0aW5nLmNvghR3d3cua2djb250cmFjdGluZy5jbzBMBgNVHSAERTBDMAgGBmeBDAECATA3BgsrBgEEAYLfEwEBATAoMCYGCCsGAQUFBwIBFhpodHRwOi8vY3BzLmxldHNlbmNyeXB0Lm9yZzCCAQMGCisGAQQB1nkCBAIEgfQEgfEA7wB1ALc++yTfnE26dfI5xbpY9Gxd/ELPep81xJ4dCYEl7bSZAAABhWgwUWYAAAQDAEYwRAIgPnPJ0efxcIewdyN8cVA54dXzbNdWNd9EAXdnInNU3X0CIBfPtneRMMSLSWhR1a65cMO0Pg+h8x1rwD8zONe4cWlHAHYA6D7Q2j71BjUy51covIlryQPTy9ERa+zraeF3fW0GvW4AAAGFaDBTWAAABAMARzBFAiEAnHKNpDyb9HALbXPDsxVbVHPWKdW48GxzNYlM5h+/OvACIC5nfWT45zaOOXabpFgS+j0KLjzOdh2OiYJ2OS1ZK1R1MA0GCSqGSIb3DQEBCwUAA4IBAQCVNHp72J2mpr2a3MUJZp2TO14qKbQUMX1ysCxYO/rb9hb1tpd4JO6ASE/krgw427EBPYlrWp2xL9xiKW+++7qE7QiabmLBSMydHmC/2c9ufRyPXg8xWHJhimgF5b9IQyzi0KrAfUq4Raf2jBphw903wOQMJrOGsfN/8vxQ5urNwwXs0T2hxDuxIJyxPFpjh8/7V/rYHQFJazxkmYF+0c8aDvgJtrQIA1td5yQjxsf4TDqelRPIn6j8Sb9vkHRlYevRtOoi51V9PlBbXs0onbuM5xxNOswuZ6J7uxLdJCyPpRLRnci3vWuIvMamSEuznIlPe3VmMKEFJamrM1kDCqKt",
    "added_at": "2023-01-06T12:46:27Z",
    "modified_at": "2023-04-01T16:18:53Z",
    "validated_at": "2023-04-01T16:18:53Z",
    "parse_status": "CERTIFICATE_PARSE_STATUS_SUCCESS",
    "zlint": {
        "version": 3,
        "timestamp": "2023-03-14T22:25:59Z",
        "notices_present": True,
        "failed_lints": ["n_subject_common_name_included"],
        "warnings_present": False,
        "errors_present": False,
        "fatals_present": False,
    },
    "precert": False,
    "revoked": False,
    "labels": [
        "untrusted",
        "ever-trusted",
        "ct",
        "leaf",
        "dv",
        "was-trusted",
        "expired",
    ],
}
VIEW_CERT_JSON = {
    "code": 200,
    "status": "OK",
    "result": EXAMPLE_CERT_JSON,
}
BULK_VIEW_CERTS_JSON = {
    "code": 200,
    "status": "OK",
    "result": [EXAMPLE_CERT_JSON],
}
SEARCH_CERTS_JSON = {
    "code": 200,
    "status": "OK",
    "result": {
        "query": TEST_SEARCH_QUERY,
        "total": 50000,
        "duration_ms": 356,
        "hits": [EXAMPLE_CERT_JSON],
        "links": {"prev": "prevCursorToken", "next": "nextCursorToken"},
    },
}
AGGREGATE_CERTS_JSON = {
    "code": 200,
    "status": "OK",
    "result": {
        "query": TEST_SEARCH_QUERY,
        "field": TEST_AGGREGATION_FIELD,
        "total": 58906,
        "duration_ms": 690,
        "buckets": [
            {"key": "Internet Widgits Pty Ltd", "count": 23748},
            {"key": "DigiCert Inc", "count": 10885},
            {"key": "QuoVadis Limited", "count": 1883},
            {"key": "Entrust, Inc.", "count": 1475},
            {"key": "Webmin", "count": 1071},
        ],
    },
}
VIEW_HOSTS_BY_CERT_JSON = {
    "code": 200,
    "status": "OK",
    "result": {
        "fp": TEST_CERT,
        "hosts": [
            {
                "ip": "string",
                "name": "string",
                "observed_at": "2021-08-02T14:56:38.711Z",
                "first_observed_at": "2021-08-02T14:56:38.711Z",
            }
        ],
        "links": {"next": "nextCursorToken"},
    },
}


class TestCerts(CensysTestCase):
    def setUp(self):
        super().setUp()
        self.setUpApi(SearchClient(self.api_id, self.api_secret).v2.certs)

    def test_view(self):
        self.responses.add(
            responses.GET,
            f"{V2_URL}/certificates/{TEST_CERT}",
            status=200,
            json=VIEW_CERT_JSON,
        )
        result = self.api.view(TEST_CERT)
        assert result == VIEW_CERT_JSON["result"]

    @parameterized.expand(
        [
            ("bulk_post"),
            ("bulk"),
            ("bulk_view"),
        ]
    )
    def test_bulk_post(self, method_name: str):
        self.responses.add(
            responses.POST,
            f"{V2_URL}/certificates/bulk",
            status=200,
            json=BULK_VIEW_CERTS_JSON,
        )
        method = getattr(self.api, method_name)
        result = method([TEST_CERT, ALTERNATE_CERT])
        assert result == BULK_VIEW_CERTS_JSON["result"]

    def test_bulk_get(self):
        certs = [TEST_CERT, ALTERNATE_CERT]
        params = {"fingerprints": certs}
        self.responses.add(
            responses.GET,
            f"{V2_URL}/certificates/bulk",
            status=200,
            json=BULK_VIEW_CERTS_JSON,
            match=[matchers.query_param_matcher(params)],
        )
        result = self.api.bulk_get(certs)
        assert result == BULK_VIEW_CERTS_JSON["result"]

    def test_bulk_get_single(self):
        params = {"fingerprints": TEST_CERT}
        self.responses.add(
            responses.GET,
            f"{V2_URL}/certificates/bulk",
            status=200,
            json=BULK_VIEW_CERTS_JSON,
            match=[matchers.query_param_matcher(params)],
        )
        result = self.api.bulk_get(TEST_CERT)
        assert result == BULK_VIEW_CERTS_JSON["result"]

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
            f"{V2_URL}/certificates/search",
            status=200,
            json=SEARCH_CERTS_JSON,
        )
        method = getattr(self.api, method_name)
        result = method(TEST_SEARCH_QUERY)
        if raw:
            assert result == SEARCH_CERTS_JSON
        else:
            assert result == SEARCH_CERTS_JSON["result"]

    def test_search(self):
        self.responses.add(
            responses.POST,
            f"{V2_URL}/certificates/search",
            status=200,
            json=SEARCH_CERTS_JSON,
        )
        query = self.api.search(TEST_SEARCH_QUERY)
        assert next(query) == SEARCH_CERTS_JSON["result"]["hits"]

    @parameterized.expand(
        [
            ({}, {"q": TEST_SEARCH_QUERY, "per_page": 50}),
            ({"per_page": 1}, {"q": TEST_SEARCH_QUERY, "per_page": 1}),
            (
                {"cursor": "nextCursorToken"},
                {"q": TEST_SEARCH_QUERY, "cursor": "nextCursorToken", "per_page": 50},
            ),
            (
                {"fields": ["names"]},
                {"q": TEST_SEARCH_QUERY, "fields": "names", "per_page": 50},
            ),
            (
                {
                    "fields": [
                        "names",
                        "fingerprint_sha256",
                        "parsed.issuer.organization",
                        "parsed.subject.postal_code",
                    ]
                },
                {
                    "q": TEST_SEARCH_QUERY,
                    "fields": [
                        "names",
                        "fingerprint_sha256",
                        "parsed.issuer.organization",
                        "parsed.subject.postal_code",
                    ],
                    "per_page": 50,
                },
            ),
            (
                {"sort": "parsed.subject.postal_code"},
                {
                    "q": TEST_SEARCH_QUERY,
                    "sort": "parsed.subject.postal_code",
                    "per_page": 50,
                },
            ),
            (
                {"sort": ["parsed.subject.postal_code", "parsed.subject.country"]},
                {
                    "q": TEST_SEARCH_QUERY,
                    "sort": ["parsed.subject.postal_code", "parsed.subject.country"],
                    "per_page": 50,
                },
            ),
        ]
    )
    def test_search_get(self, params: Dict[str, Any], expected_params: Dict[str, Any]):
        self.responses.add(
            responses.GET,
            f"{V2_URL}/certificates/search",
            status=200,
            json=SEARCH_CERTS_JSON,
            match=[matchers.query_param_matcher(expected_params)],
        )
        result = self.api.search_get(TEST_SEARCH_QUERY, **params)
        assert result == SEARCH_CERTS_JSON["result"]

    def test_aggregate(self):
        params = {
            "q": TEST_SEARCH_QUERY,
            "field": TEST_AGGREGATION_FIELD,
            "num_buckets": 50,
        }
        self.responses.add(
            responses.GET,
            f"{V2_URL}/certificates/aggregate",
            status=200,
            json=AGGREGATE_CERTS_JSON,
            match=[matchers.query_param_matcher(params)],
        )
        result = self.api.aggregate(TEST_SEARCH_QUERY, TEST_AGGREGATION_FIELD)
        assert result == AGGREGATE_CERTS_JSON["result"]

    def test_get_hosts_by_cert(self):
        self.responses.add(
            responses.GET,
            f"{V2_URL}/certificates/{TEST_CERT}/hosts",
            status=200,
            json=VIEW_HOSTS_BY_CERT_JSON,
        )
        result = self.api.get_hosts_by_cert(TEST_CERT)
        assert result == VIEW_HOSTS_BY_CERT_JSON["result"]

    def test_get_hosts_by_cert_with_cursor(self):
        self.responses.add(
            responses.GET,
            f"{V2_URL}/certificates/{TEST_CERT}/hosts?cursor=nextCursorToken",
            status=200,
            json=VIEW_HOSTS_BY_CERT_JSON,
        )
        results = self.api.get_hosts_by_cert(TEST_CERT, cursor="nextCursorToken")
        assert results == VIEW_HOSTS_BY_CERT_JSON["result"]
