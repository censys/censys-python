# Censys Python Library

[![PyPI](https://img.shields.io/pypi/v/censys?color=orange&logo=pypi&logoColor=orange)](https://pypi.org/project/censys/)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue?logo=python)](https://www.python.org/downloads/)
[![Read the Docs (version)](https://img.shields.io/readthedocs/censys-python/latest?logo=read%20the%20docs)](https://censys-python.readthedocs.io/en/stable/?badge=stable)
[![GitHub Discussions](https://img.shields.io/badge/GitHub-Discussions-brightgreen?logo=github)](https://github.com/censys/censys-python/discussions)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-organge.svg?logo=git&logoColor=organge)](http://makeapullrequest.com)
[![License](https://img.shields.io/github/license/censys/censys-python?logo=apache)](https://github.com/censys/censys-python/blob/main/LICENSE)

An easy-to-use and lightweight API wrapper for Censys APIs ([censys.io](https://censys.io/)). Python 3.6+ is currently supported.

> **Notice:** The Censys Search v1 endpoints are going away on Nov. 30, 2021. Please begin using v2 endpoints to query hosts and certificates and check out our [support center](https://support.censys.io/hc/en-us/sections/360013076551-Censys-Search-2-0) for resources.

## Features

- [Search Censys data](https://censys-python.readthedocs.io/en/stable/usage-v2.html)
- [Bulk Certificate lookups](https://censys-python.readthedocs.io/en/stable/usage-v1.html#bulk)
- [Download Bulk Data](https://censys-python.readthedocs.io/en/stable/usage-v1.html#data)
- [Manage assets, events, and seeds in Censys ASM](https://censys-python.readthedocs.io/en/stable/usage-asm.html)
- [Command-line interface](https://censys-python.readthedocs.io/en/stable/cli.html)

<a href="https://asciinema.org/a/418153" target="_blank"><img src="https://asciinema.org/a/418153.svg" width="600"/></a>

## Getting Started

The library can be installed using `pip`.

```bash
pip install censys
```

To upgraded using `pip`.

```bash
pip install --upgrade censys
```

To configure your search credentials run `censys config` or set both `CENSYS_API_ID` and `CENSYS_API_SECRET` environment variables.

```bash
$ censys config

Censys API ID: XXX
Censys API Secret: XXX

Successfully authenticated for your@email.com
```

To configure your ASM credentials run `censys asm config` or set the `CENSYS_ASM_API_KEY` environment variables.

```bash
$ censys asm config

Censys ASM API Key: XXX

Successfully authenticated
```

## API Reference and User Guide available on [Read the Docs](https://censys-python.readthedocs.io/)

[![Read the Docs](https://raw.githubusercontent.com/censys/censys-python/main/docs/_static/readthedocs.png)](https://censys-python.readthedocs.io/)

## Resources

- [Source](https://github.com/censys/censys-python)
- [Issue Tracker](https://github.com/censys/censys-python/issues)
- [Changelog](https://github.com/censys/censys-python/releases)
- [Documentation](https://censys-python.rtfd.io)
- [Discussions](https://github.com/censys/censys-python/discussions)
- [Censys Homepage](https://censys.io/)

## Contributing

All contributions (no matter how small) are always welcome.

## Development

This project uses [poetry](https://python-poetry.org/) for dependency management. Please ensure you have [installed the latest version](https://python-poetry.org/docs/#installation).

```bash
git clone git@github.com:censys/censys-python.git
cd censys-python/
poetry install
```

## Testing

```bash
pytest
# With coverage report
pytest --cov-report html
```

## License

This software is licensed under [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)

- Copyright (C) 2021 Censys, Inc.
