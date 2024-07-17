import importlib
import os
import sys

import pytest
from typer import Typer
from typer.testing import CliRunner


@pytest.fixture(scope="session")
def app() -> Typer:
    # Update the import path so we can import it
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parentdir)

    main = importlib.import_module("s3-to-s3")
    return main.app


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()
