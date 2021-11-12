import os
import zipfile

import pytest

from pyflp import Parser, Project

curdir = os.path.dirname(__file__)
zp = zipfile.ZipFile(f"{curdir}/assets/FL 20.8.3.zip")


@pytest.fixture(autouse=True, scope="session")
def proj() -> Project:
    return Parser().parse_zip(zp)