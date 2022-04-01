<!-- PROJECT SHIELDS -->

![GitHub Workflow Status][workflow-shield]
[![Documentation Status][docs-shield]][docs-link]
[![codecov][codecov-badge]][codecov-link]
[![CodeFactor][codefactor-badge]][codefactor-link]
[![Gitter chat][gitter-badge]][gitter-link]
[![PyPI - License][license-shield]][license-link]
![PyPI - Version][version-shield]
![PyPI - Python Version][pyversions-shield]
[![Contributor Covenant][covenant-shield]][covenant-link]
[![Code Style: Black][black-shield]][black-link]

# PyFLP

PyFLP is a parser written in Python for FL Studio project (.flp) files.

You should also check some of my other projects based on PyFLP:

- A CLI utility [FLPInfo](https://github.com/demberto/FLPInfo) to see basic
  information about an FLP.
- A GUI tool [FLPInspect](https://github.com/demberto/FLPInspect) for a
  further, detailed view into the internal structure of an FLP.

## ⏬ Installation

PyFLP requires Python 3.6+

```
pip install --upgrade pyflp
```

## ▶ Usage

### Initialisation

```Python
from pyflp import Parser
project = Parser().parse("/path/to/efelpee.flp")
```

More examples [here](https://pyflp.rtfd.io/en/latest/handbook/)

## 📜 Documentation

Docs are available on [ReadTheDocs](https://pyflp.rtfd.io)

## 🙏 Thanks

[**Monad.FLParser**](https://github.com/monadgroup/FLParser)

**FLPEdit** [(author)](https://github.com/roadcrewworker)

## 🤝 [Contributing](https://github.com/demberto/PyFLP/blob/master/CONTRIBUTING.md)

## [Changelog](https://github.com/demberto/PyFLP/blob/master/CHANGELOG.md)

## © License

**PyFLP** has been licensed under the [GNU Public License v3][gpl3-link].

<!-- BADGES / SHIELDS -->
[black-shield]: https://img.shields.io/badge/code%20style-black-black
[codecov-badge]: https://codecov.io/gh/demberto/PyFLP/branch/master/graph/badge.svg?token=RGSRMMF8PF
[codefactor-badge]: https://www.codefactor.io/repository/github/demberto/pyflp/badge
[covenant-shield]: https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg
[docs-shield]: https://readthedocs.org/projects/pyflp/badge/?version=latest
[gitter-badge]: https://badges.gitter.im/gitterHQ/gitter.png
[license-shield]: https://img.shields.io/pypi/l/pyflp
[pyversions-shield]: https://img.shields.io/pypi/pyversions/pyflp
[version-shield]: https://img.shields.io/pypi/v/pyflp
[workflow-shield]: https://img.shields.io/github/workflow/status/demberto/pyflp/main

<!-- LINKS -->
[black-link]: https://github.com/psf/black
[codecov-link]: https://codecov.io/gh/demberto/PyFLP
[codefactor-link]: https://www.codefactor.io/repository/github/demberto/pyflp
[covenant-link]: https://github.com/demberto/PyFLP/blob/master/CODE_OF_CONDUCT.md
[docs-link]: https://pyflp.readthedocs.io/en/latest/
[gitter-link]: https://gitter.im/PyFLP/community
[gpl3-link]: https://www.gnu.org/licenses/gpl-3.0.en.html
[license-link]: https://github.com/demberto/PyFLP/blob/master/LICENSE
