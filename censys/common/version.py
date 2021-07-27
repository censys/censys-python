"""Censys Version."""
try:
    import importlib_metadata
except ImportError:
    import importlib.metadata as importlib_metadata  # type: ignore

__version__: str = importlib_metadata.version("censys")
