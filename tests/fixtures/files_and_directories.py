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

DATA_DIR = Path(f"{TEST_DIR}/data")

DATA_FILE = Path(
    str(
        f"{DATA_DIR}/{TICKER}-"
        f"{ValidYahooApiFrequencies.ONE_DAY.value}-"
        f"{START_DATE}-{END_DATE}.csv",
    ),
)

PLOT_DIR = Path(f"{TEST_DIR}/plots")


@pytest.fixture(scope="session", autouse=True)
def _clean_data() -> Generator[None, None, None]:
    """Clean temp test data directory after tests."""
    yield
    rmtree(TEST_DIR)
