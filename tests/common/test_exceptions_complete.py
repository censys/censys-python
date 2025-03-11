"""Tests for the Censys Exceptions module with focus on complete coverage."""

from censys.common.exceptions import (
    CensysAPIException,
    CensysExceptionMapper,
    CensysUnauthorizedException,
)


def test_get_exception_class_platform_exception():
    """Test that get_exception_class returns a platform exception when status code matches."""
    # Use 401 which is a known platform exception
    exception_class = CensysExceptionMapper._get_exception_class(401, "platform")
    assert exception_class == CensysUnauthorizedException


def test_get_exception_class_search_exception():
    """Test that get_exception_class returns a search exception when status code matches."""
    # Use 401 which is a known search exception
    exception_class = CensysExceptionMapper._get_exception_class(401, "search")
    assert exception_class == CensysUnauthorizedException


def test_get_exception_class_fallback():
    """Test that get_exception_class falls back to CensysAPIException for unknown status codes."""
    # Use 599 which is not a known exception code
    exception_class = CensysExceptionMapper._get_exception_class(599, "platform")
    assert exception_class == CensysAPIException
