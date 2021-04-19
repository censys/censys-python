"""Censys Python Setup."""
import os
from setuptools import find_packages, setup

NAME = "censys"
DESCRIPTION = "An easy-to-use and lightweight API wrapper for Censys APIs (censys.io)."
GIT_URL = "https://github.com/censys/censys-python"
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
    keywords=NAME,
    python_requires=">=3.6.0",
    packages=find_packages(exclude=["tests", "examples"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=["requests>=2.25.1", "backoff==1.10.0"],
    extras_require={
        "dev": [
            "flake8==3.9.1",
            "flake8-docstrings==1.6.0",
            "flake8-pytest-style==1.4.1",
            "flake8-simplify==0.14.0",
            "flake8-comprehensions==3.4.0",
            "pep8-naming==0.11.1",
            "flake8-black==0.2.1",
            "black==20.8b1",
            "pytest==6.2.3",
            "pytest-cov==2.11.1",
            "responses==0.13.2",
            "mypy==0.812",
            "backoff-stubs==1.10.0",
            "twine==3.4.1",
            "parameterized==0.8.1",
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
    project_urls={
        "Censys Homepage": "https://censys.io/",
        "Documentation": DOC_URL,
        "Changelog": GIT_URL + "/releases",
        "Tracker": GIT_URL + "/issues",
        "Source": GIT_URL,
    },
)
