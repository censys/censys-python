from typing import Optional


class CensysException(Exception):
    pass


class CensysAPIException(CensysException):
    def __init__(
        self,
        status_code: int,
        message: str,
        headers: Optional[dict] = None,
        body: Optional[str] = None,
        const: Optional[str] = None,
    ):
        self.status_code = status_code
        self.message = message
        self.headers = headers or {}
        self.body = body
        self.const = const

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
