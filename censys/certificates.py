import unittest

from .base import CensysAPIBase, CensysIndex, CensysException


class CensysCertificates(CensysIndex):

    INDEX_NAME = "certificates"


class CensysCertificatesTests(unittest.TestCase):
    correct_search_result = {u'parsed.fingerprint_sha256': u'fce621c0dc1c666d03d660472f636ce91e66e96460545f0da7eb1a24873e2f70', 
        u'parsed.subject_dn': u'CN=ns1.google.com, emailAddress=ssl@ns1.google.com'}

    correct_get_result = {
        "tags": ["unknown", "expired", "self-signed"],
        "raw": "MIIDQzCCAiugAwIBAgIEdGWCQjANBgkqhkiG9w0BAQsFADA8MRcwFQYDVQQDDA5uczEuZ29vZ2xlLmNvbTEhMB8GCSqGSIb3DQEJARYSc3NsQG5zMS5nb29nbGUuY29tMB4XDTE1MDkxMDA2NDkxOVoXDTE2MDkwOTA2NDkxOVowPDEXMBUGA1UEAwwObnMxLmdvb2dsZS5jb20xITAfBgkqhkiG9w0BCQEWEnNzbEBuczEuZ29vZ2xlLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAL2I5uWRiHRJNVqO26HZybIijYqj2aBLFF6qA1fkxqSMQmSpBgd6CbHKB2g2Lm1QVBbrnPuv07Q9+9YRFiPGjITwP0IUQbWbig11MoCIB8tfEgRtnIiW+8XESAXTvRTZrKX5cRV+aCz21XPi41z8+QrNSd3QEqofkA1o3Xb5jGkYOlPqEB5kTmKt26PjY5RfjxXOlyfs7oPVQxKaTSob4MPN2BTmkvqJWyi7rN+E8Vtgte0NKvAAWrJ9xg36fjuYsWR5HzCVNYK7K0GUdvaB5IAueDcrThYYloy6ErJWGOYhWUT5w6+BrRmc15q2Vz8MIjVKiNqGrmfJtNrWsghD3y8CAwEAAaNNMEswHQYDVR0OBBYEFNw+Lj9JsSZ4Ly3UREw8tZcL6Fl5MB8GA1UdIwQYMBaAFNw+Lj9JsSZ4Ly3UREw8tZcL6Fl5MAkGA1UdEwQCMAAwDQYJKoZIhvcNAQELBQADggEBAC3r3hrkO51YX7AhfDX6sremmu9KQMHYcpMQHCrMsn2SEXqLYWW4fe/abEfZ2ADpG7G/c8Tevc5auyBEfEUMej6ZcOPQeHElXc+v8xVdUVwmKNlWYVV6b0FMT9Uzt1DP3C6sFnXURzX5tCVjf1r2Ef5DUPgZrYiqmVFjZ1rCoVTZ6Envy7pG3GWrwD6WPtx5BYkT0yPWn38RUZ5hY3Uyx5Zw1zYFqrY6xEBN8D+hvfFlwKIYn/goD/eoW6Htau2CJK8yoG0WjKCXrSQGoZ8PRnOfZ2YGiodtOSXkZxTNXnjgf4sRV3tZD/AkgBnuQZHfttTb1KF5dk3lpNMGNlnG9rw=",
        "parents": [],
        "precert": False,
        "validation": {
            "google_ct_primary": {
                "paths": [],
                "blacklisted": False,
                "had_trusted_path": False,
                "whitelisted": False,
                "in_revocation_set": False,
                "was_valid": False,
                "valid": False,
                "parents": [],
                "trusted_path": False,
                "type": "unknown",
            },
            "nss": {
                "paths": [],
                "blacklisted": False,
                "had_trusted_path": False,
                "whitelisted": False,
                "in_revocation_set": False,
                "was_valid": False,
                "valid": False,
                "parents": [],
                "trusted_path": False,
                "type": "unknown",
            },
            "apple": {
                "paths": [],
                "blacklisted": False,
                "had_trusted_path": False,
                "whitelisted": False,
                "in_revocation_set": False,
                "was_valid": False,
                "valid": False,
                "parents": [],
                "trusted_path": False,
                "type": "unknown",
            },
            "microsoft": {
                "paths": [],
                "blacklisted": False,
                "had_trusted_path": False,
                "whitelisted": False,
                "in_revocation_set": False,
                "was_valid": False,
                "valid": False,
                "parents": [],
                "trusted_path": False,
                "type": "unknown",
            },
        },
        "parsed": {
            "tbs_noct_fingerprint": "e9bae1d0af98bfebcb73d061e2b5088d33ecf4e29646b5afbcc9b0026f9f8641",
            "subject_dn": "CN=ns1.google.com, emailAddress=ssl@ns1.google.com",
            "subject": {
                "common_name": ["ns1.google.com"],
                "email_address": ["ssl@ns1.google.com"],
            },
            "redacted": False,
            "signature": {
                "self_signed": True,
                "valid": False,
                "value": "LeveGuQ7nVhfsCF8Nfqyt6aa70pAwdhykxAcKsyyfZIReothZbh979psR9nYAOkbsb9zxN69zlq7IER8RQx6Pplw49B4cSVdz6/zFV1RXCYo2VZhVXpvQUxP1TO3UM/cLqwWddRHNfm0JWN/WvYR/kNQ+BmtiKqZUWNnWsKhVNnoSe/LukbcZavAPpY+3HkFiRPTI9affxFRnmFjdTLHlnDXNgWqtjrEQE3wP6G98WXAohif+CgP96hboe1q7YIkrzKgbRaMoJetJAahnw9Gc59nZgaKh205JeRnFM1eeOB/ixFXe1kP8CSAGe5Bkd+21NvUoXl2TeWk0wY2Wcb2vA==",
                "signature_algorithm": {
                    "oid": "1.2.840.113549.1.1.11",
                    "name": "SHA256-RSA",
                },
            },
            "__expanded_names": ["google.com", "com", "ns1.google.com"],
            "serial_number": "1952809538",
            "validity": {
                "start": "2015-09-10T06:49:19Z",
                "length": 31536000,
                "end": "2016-09-09T06:49:19Z",
            },
            "issuer_dn": "CN=ns1.google.com, emailAddress=ssl@ns1.google.com",
            "fingerprint_sha1": "3704a663ed5db89f85c5377852d678b299389775",
            "version": 3,
            "fingerprint_sha256": "fce621c0dc1c666d03d660472f636ce91e66e96460545f0da7eb1a24873e2f70",
            "names": ["ns1.google.com"],
            "tbs_fingerprint": "e9bae1d0af98bfebcb73d061e2b5088d33ecf4e29646b5afbcc9b0026f9f8641",
            "validation_level": "unknown",
            "extensions": {
                "authority_key_id": "dc3e2e3f49b126782f2dd4444c3cb5970be85979",
                "subject_key_id": "dc3e2e3f49b126782f2dd4444c3cb5970be85979",
                "basic_constraints": {"is_ca": False},
            },
            "fingerprint_md5": "37ec912bf30802fd4ab3592f8713ef6f",
            "subject_key_info": {
                "fingerprint_sha256": "5cbcb9740f3d8a447d4267722092ad405701c6036d93b1a84c512ebefbcbe346",
                "key_algorithm": {"name": "RSA"},
                "rsa_public_key": {
                    "length": 2048,
                    "modulus": "vYjm5ZGIdEk1Wo7bodnJsiKNiqPZoEsUXqoDV+TGpIxCZKkGB3oJscoHaDYubVBUFuuc+6/TtD371hEWI8aMhPA/QhRBtZuKDXUygIgHy18SBG2ciJb7xcRIBdO9FNmspflxFX5oLPbVc+LjXPz5Cs1J3dASqh+QDWjddvmMaRg6U+oQHmROYq3bo+NjlF+PFc6XJ+zug9VDEppNKhvgw83YFOaS+olbKLus34TxW2C17Q0q8ABasn3GDfp+O5ixZHkfMJU1grsrQZR29oHkgC54NytOFhiWjLoSslYY5iFZRPnDr4GtGZzXmrZXPwwiNUqI2oauZ8m02tayCEPfLw==",
                    "exponent": 65537,
                },
            },
            "signature_algorithm": {
                "oid": "1.2.840.113549.1.1.11",
                "name": "SHA256-RSA",
            },
            "spki_subject_fingerprint": "28359cf3792cf85e8aca5cb9f3eaf6b37c1784892b9782100e8df47568201af8",
            "issuer": {
                "common_name": ["ns1.google.com"],
                "email_address": ["ssl@ns1.google.com"],
            },
        },
        "metadata": {
            "post_processed": False,
            "parse_status": "success",
            "updated_at": "2018-08-31T14:06:01",
            "source": "scan",
            "seen_in_scan": True,
            "parse_version": 0,
        },
    }

    @classmethod
    def setUpClass(cls):
        cls._api = CensysCertificates()

    def testGet(self):
        self.assertEqual(
            self._api.view("fce621c0dc1c666d03d660472f636ce91e66e96460545f0da7eb1a24873e2f70"),
            self.correct_get_result,
        )

    def testSearch(self):
        # searching for something that won't change hopefully
        x = self._api.search("fce621c0dc1c666d03d660472f636ce91e66e96460545f0da7eb1a24873e2f70", 
                            fields=["parsed.subject_dn",
                                    "parsed.fingerprint_sha256"],
                            max_records=10)
        result = list(x)
        self.assertEquals(result[0], self.correct_search_result)
        self.assertEqual(len(result), 1)

    # def testMultiplePages(self):
    #     q = "parsed.extensions.basic_constraints.is_ca: true AND parsed.signature.self_signed: false"
    #     x = self._api.search(q, page=1)
    #     y = self._api.search(q, page=2)
    #     self.assertNotEqual(list(x), list(y))

    # def testReport(self):
    #    print self._api.report("*", "parsed.subject_key_info.key_algorithm.name")


if __name__ == "__main__":
    unittest.main()
