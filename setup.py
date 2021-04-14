"""Censys Python Setup."""
import os
from setuptools import find_packages, setup

NAME = "censys"
DESCRIPTION = "An easy-to-use and lightweight API wrapper for Censys APIs (censys.io)."
GIT_URL = "https://github.com/censys/censys-python"
ISSUE_URL = GIT_URL + "/issues"
DOC_URL = "https://censys-python.rtfd.io"

here = os.path.abspath(os.path.dirname(__file__))

pkg_vars = {}  # type: ignore

with open(os.path.join(here, NAME, "version.py")) as f:
    exec(f.read(), pkg_vars)

with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

setup(
    name=NAME,
    version=pkg_vars["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Censys Team",
    author_email="support@censys.io",
    license="Apache License, Version 2.0",
    url=GIT_URL,
    keywords=NAME,
    python_requires=">=3.6.0",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=["requests", "backoff"],
    extras_require={
        "dev": [
            "flake8",
            "flake8-docstrings",
            "flake8-pytest-style",
            "flake8-simplify",
            "black",
            "pytest",
            "pytest-cov",
            "responses",
            "mypy",
            "backoff-stubs",
            "twine",
            "parameterized",
        ],
        "docs": ["sphinx"],
    },
    entry_points={"console_scripts": ["censys = censys.cli:main"]},
    classifiers=[
        "Typing :: Typed",
        "Topic :: Internet",
        "Topic :: Security",
        "Topic :: Documentation :: Sphinx",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Pytest",
        "Framework :: Flake8",
        "Environment :: Console",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    project_urls={"Documentation": DOC_URL, "Source": GIT_URL, "Tracker": ISSUE_URL},
)
