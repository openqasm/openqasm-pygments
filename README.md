# Pygments tools for OpenQASM

[![License](https://img.shields.io/github/license/openqasm/openqasm-pygments.svg?style=popout-square)](https://opensource.org/licenses/Apache-2.0)<!--- long-description-skip-begin -->[![Release](https://img.shields.io/github/release/openqasm/openqasm-pygments.svg?style=popout-square)](https://github.com/openqasm/openqasm-pygments/releases)[![Downloads](https://img.shields.io/pypi/dm/openqasm-pygments.svg?style=popout-square)](https://pypi.org/project/openqasm-pygments/)<!--- long-description-skip-end -->

This repository provides the Python package `openqasm-pygments`, which provides
a lexer for syntax highlighting OpenQASM code with [Pygments](https://pygments.org/).
There are current three lexers included, all of which register themselves with
Pygments when this package is installed:

- `OpenQASM3Lexer` (Pygments aliases `openqasm3` and `qasm3`), for parsing
  OpenQASM 3 code.  Most OpenQASM 2 programs will lex acceptably with this lexer
  as well, except for some keyword differences.
- `OpenQASM2Lexer` (aliases `openqasm2` and `qasm2`), for lexing OpenQASM 2
  programs.
- `OpenPulseLexer` (aliases `openpulse`), for lexing the OpenPulse pulse
  calibration dialect also defined in the OpenQASM 3 specification.  For the
  most part, this lexer will not be used as a root, but the `OpenQASM3Lexer`
  will delegate lexing of calibration blocks to it, when required.


## Installation

Install the latest release of `openqasm-pygments` package from pip:

```bash
pip install openqasm-pygments
```

This will automatically install all the dependencies as well (Pygments, for
example) if they are not already installed.


## Developing

If you're looking to contribute to this project, please first read
[our contributing guidelines](CONTRIBUTING.md).

Set up your development environment by installing the development requirements
with pip:

```bash
pip install -r requirements-dev.txt tox
```

This installs a few more packages than the dependencies of the package at
runtime, because there are some tools we use for testing also included, such as
`tox` and `pytest`.

After the development requirements are installed, you can install an editable
version of the package with

```bash
pip install -e .
```

After this, any changes you make to the library code will immediately be present
when you open a new Python interpreter session.


## License

This project is licensed under [version 2.0 of the Apache License](LICENSE).
This is a Qiskit project.
