"""
Exceptions for Censys.

Classes:
    CensysException
    CensysAPIException
    CensysRateLimitExceededException
    CensysNotFoundException
    CensysUnauthorizedException
    CensysJSONDecodeException
    CensysCLIException
"""

from typing import Optional


class CensysException(Exception):
    pass


class CensysAPIException(CensysException):
    def __init__(
        self,
        status_code: int,
        message: str,
        body: Optional[str] = None,
        const: Optional[str] = None,
    ):
        self.status_code = status_code
        self.message = message
        self.body = body
        self.const = const
        super().__init__(self.message)

    def __repr__(self):
        return "%i (%s): %s" % (self.status_code, self.const, self.message or self.body)

    __str__ = __repr__


class CensysRateLimitExceededException(CensysAPIException):
    pass


class CensysNotFoundException(CensysAPIException):
    pass


class CensysUnauthorizedException(CensysAPIException):
    pass


class CensysJSONDecodeException(CensysAPIException):
    pass


class CensysCLIException(Exception):
    pass
