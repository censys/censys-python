# Censys Python Library

[![PyPI](https://img.shields.io/pypi/v/censys?color=orange)](https://pypi.org/project/censys/)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/censys/censys-python)](LICENSE)
[![Documentation](https://readthedocs.org/projects/censys-python/badge/?version=latest)](https://censys-python.readthedocs.io/en/latest/?badge=latest)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

An easy-to-use and lightweight API wrapper for the Censys Search Engine ([censys.io](https://censys.io/)). Python 3.6+ is currently supported.

## Getting Started

The library can be installed using `pip`.

```bash
$ pip install censys
```

To configure your credentials run `censys config` or set both `CENSYS_API_ID` and `CENSYS_API_SECRET` environment variables.

```bash
$ censys config

Censys API ID: XXX
Censys API Secret: XXX

Successfully authenticated for your@email.com
```

## Resources

- [Official Website](https://censys.io/)
- [Documentation](https://censys-python.rtfd.io)
- [Issue Tracker](https://github.com/censys/censys-python/issues)

## Contributing

All contributions (no matter how small) are always welcome.

## Development

```bash
$ git clone git@github.com:censys/censys-python.git
$ pip install -e ".[dev]"
```

## Testing

Testing requires credentials to be set.

```bash
$ pytest
```
