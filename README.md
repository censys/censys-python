# Censys Python Library

[![PyPI](https://img.shields.io/pypi/v/censys?color=orange&logo=pypi&logoColor=orange)](https://pypi.org/project/censys/)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue?logo=python)](https://www.python.org/downloads/)
[![Read the Docs (version)](https://img.shields.io/readthedocs/censys-python/latest?logo=read%20the%20docs)](https://censys-python.readthedocs.io/en/stable/?badge=stable)
[![GitHub Discussions](https://img.shields.io/badge/GitHub-Discussions-brightgreen?logo=github)](https://github.com/censys/censys-python/discussions)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-organge.svg?logo=git&logoColor=organge)](http://makeapullrequest.com)
[![License](https://img.shields.io/github/license/censys/censys-python?logo=apache)](https://github.com/censys/censys-python/blob/main/LICENSE)

> [!WARNING]
> **DEPRECATION NOTICE**: The Censys Search v1 and v2 APIs will be deprecated soon. Please migrate to the new **Censys Platform**.
> 
> - 📖 **New API Documentation**: [https://docs.censys.com/reference/get-started#/](https://docs.censys.com/reference/get-started#/)
> - 📦 **New Python SDK**: Install with `pip install censys-platform` - [https://pypi.org/project/censys-platform/](https://pypi.org/project/censys-platform/)
> - 🖥️ **New CLI Tool** (`cencli`): [https://docs.censys.com/docs/platform-cli](https://docs.censys.com/docs/platform-cli)
>   - ⚠️ **If you plan to use the new CLI, you will need to uninstall this package's CLI first** as both use the `censys` command name
> 
> The **Censys ASM APIs in this library are NOT deprecated** and will continue to be supported.

An easy-to-use and lightweight API wrapper for Censys APIs ([censys.io](https://censys.io/)). Python 3.8+ is currently supported. This library has been tested on Python 3.8 and 3.x (Currently version 3.10).

## Features

- [Search Censys data](https://censys-python.readthedocs.io/en/stable/usage-v2.html)
- [Bulk Certificate lookups](https://censys-python.readthedocs.io/en/stable/usage-v2.html#bulk-view)
- [Download Bulk Data](https://censys-python.readthedocs.io/en/stable/usage-v1.html#data)
- [Manage assets, events, and seeds in Censys ASM](https://censys-python.readthedocs.io/en/stable/usage-asm.html)
- [Command-line interface](https://censys-python.readthedocs.io/en/stable/cli.html)

<!-- markdownlint-disable MD033 -->

<a href="https://asciinema.org/a/500416" target="_blank"><img src="https://asciinema.org/a/500416.svg" width="600"/></a>

<!-- markdownlint-enable MD033 -->

## Getting Started

The library can be installed using `pip`.

```sh
pip install censys
```

To upgraded using `pip`.

```sh
pip install --upgrade censys
```

Alternatively, you can install the library using `poetry`.

```sh
git clone https://github.com/censys/censys-python.git
cd censys-python/
poetry install
```

Optionally, you can enable tab completion for the CLI by adding this line to your `~/.bashrc`, `~/.zshrc`, or equivalent.

> Please note that autocomplete is supported for field names in the `search` command.

```sh
eval "$(register-python-argcomplete censys)"
```

To configure your search credentials run `censys config` or set both `CENSYS_API_ID` and `CENSYS_API_SECRET` environment variables.

```sh
$ censys config

Censys API ID: XXX
Censys API Secret: XXX
Do you want color output? [y/n]: y

Successfully authenticated for your@email.com
```

If you have a Censys ASM account, you can configure your ASM credentials by running `censys asm config` or set both `CENSYS_ASM_API_KEY` environment variables.

```sh
$ censys asm config

Censys ASM API Key: XXX
Do you want color output? [y/n]: y

Successfully authenticated
```

## Examples

The examples located in the [`examples/`](examples/) directory are a great place to start. You can also find more examples in the [usage documentation](https://censys-python.readthedocs.io/en/stable/usage-v2.html).

## [Documentation](https://censys-python.readthedocs.io/)

[![Read the Docs](https://raw.githubusercontent.com/censys/censys-python/main/docs/_static/readthedocs.png)](https://censys-python.readthedocs.io/)

## Resources

- [Source](https://github.com/censys/censys-python)
- [Issue Tracker](https://github.com/censys/censys-python/issues)
- [Changelog](https://github.com/censys/censys-python/releases)
- [Documentation](https://censys-python.rtfd.io)
- [Discussions](https://github.com/censys/censys-python/discussions)
- [Censys Homepage](https://censys.io/)
- [Censys Search](https://search.censys.io/)

## Contributing

All contributions (no matter how small) are always welcome. See [Contributing to Censys Python](.github/CONTRIBUTING.md)

## Development

This project uses [poetry](https://python-poetry.org/) for dependency management. Please ensure you have [installed the latest version](https://python-poetry.org/docs/#installation).

```sh
git clone git@github.com:censys/censys-python.git
cd censys-python/
poetry install
```

## Testing

```sh
# Run tests
poetry run pytest
# With coverage report
poetry run pytest --cov-report html
```

## License

This software is licensed under [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)

- Copyright (C) 2024 Censys, Inc.
