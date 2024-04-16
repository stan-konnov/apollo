from os import curdir
from pathlib import Path
from shutil import rmtree
from typing import Generator

import pytest

from apollo.settings import (
    END_DATE,
    START_DATE,
    TICKER,
    ValidYahooApiFrequencies,
)

TEST_DIR = Path(f"{Path(curdir).resolve()}/tests/temp")
DATA_FIL = Path(
    str(
        f"{TEST_DIR}/{TICKER}-"
        f"{ValidYahooApiFrequencies.ONE_DAY.value}-"
        f"{START_DATE}-{END_DATE}.csv",
    ),
)


@pytest.fixture(name="data_file", scope="session")
def get_data_file() -> Path:
    """Fixture to get data file."""
    return DATA_FIL


@pytest.fixture(scope="session", autouse=True)
def _clean_data() -> Generator[None, None, None]:
    """Clean temp test data directory after tests."""
    yield
    rmtree(TEST_DIR)
