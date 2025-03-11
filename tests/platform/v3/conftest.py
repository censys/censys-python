"""Configuration for platform v3 tests."""
import pytest


def pytest_configure(config):
    """Register custom markers for pytest.

    Args:
        config: The pytest config object
    """
    config.addinivalue_line(
        "markers",
        "e2e: marks end-to-end tests that make real API calls and should be run manually, not in CI",
    )


def pytest_collection_modifyitems(config, items):
    """Modify collected test items before running tests.

    This hook skips all e2e tests by default unless the --run-e2e flag is provided.

    Args:
        config: The pytest config object
        items: List of collected test items
    """
    if hasattr(config.option, "run_e2e") and not config.option.run_e2e:
        skip_e2e = pytest.mark.skip(
            reason="Need --run-e2e option to run end-to-end tests"
        )
        for item in items:
            if "e2e" in item.keywords:
                item.add_marker(skip_e2e)
