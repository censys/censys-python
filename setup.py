import io
import os
from setuptools import setup, find_packages

import censys

NAME = "censys"
DESCRIPTION = censys.__doc__.strip()
URL = "https://github.com/censys/censys-python"

REQUIRES_PYTHON = ">=3.6.0"
REQUIRED = ["requests", "netaddr"]
EXTRAS = {
    "dev": ["flake8", "black", "pytest", "pytest-cov", "mypy", "twine"],
}

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

setup(
    name=NAME,
    version=censys.__version__,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=censys.__author__,
    author_email=censys.__email__,
    license=censys.__license__,
    url=URL,
    keywords=NAME,
    python_requires=REQUIRES_PYTHON,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    entry_points={"console_scripts": ["censys = censys.cli:main",]},
    classifiers=[
        "Typing :: Typed",
        "Topic :: Internet",
        "Topic :: Security",
        "Framework :: Pytest",
        "Framework :: Flake8",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: PyPy",
        "License :: OSI Approved :: Apache Software License",
    ],
)
