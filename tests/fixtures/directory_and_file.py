from os import curdir
from pathlib import Path
from shutil import rmtree
from typing import Generator
from unittest.mock import patch

import pytest

from apollo.settings import (
    END_DATE,
    START_DATE,
    TICKER,
    ValidYahooApiFrequencies,
)

DATA_DIR = Path(f"{Path(curdir).resolve()}/tests/temp")
DATA_FIL = Path(
    str(
        f"{DATA_DIR}/{TICKER}-"
        f"{ValidYahooApiFrequencies.ONE_DAY.value}-"
        f"{START_DATE}-{END_DATE}.csv",
    ),
)

@pytest.fixture(name="data_dir", scope="session")
def _get_data_dir() -> Generator[None, None, None]:
    """Fixture to get data directory."""

    with patch("apollo.api.yahoo_api_connector.DATA_DIR", DATA_DIR):
        yield


@pytest.fixture(name="data_file", scope="session")
def get_data_file() -> Path:
    """Fixture to get data file."""

    return DATA_FIL


@pytest.fixture(scope="session", autouse=True)
def _clean_data() -> Generator[None, None, None]:
    """Clean temp test data directory after tests."""

    yield
    rmtree(DATA_DIR)
