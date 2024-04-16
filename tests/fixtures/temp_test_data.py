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

TEMP_TEST_DATA_DIR = Path(f"{Path(curdir).resolve()}/tests/temp")
TEMP_TEST_DATA_FILE = Path(
    str(
        f"{TEMP_TEST_DATA_DIR}/{TICKER}-"
        f"{ValidYahooApiFrequencies.ONE_DAY.value}-"
        f"{START_DATE}-{END_DATE}.csv",
    ),
)

@pytest.fixture(name="temp_test_data_dir", scope="session")
def _get_temp_test_data_dir() -> Generator[None, None, None]:
    """Fixture to get test temp data directory."""

    with patch("apollo.api.yahoo_api_connector.DATA_DIR", TEMP_TEST_DATA_DIR):
        yield


@pytest.fixture(name="temp_test_data_file", scope="session")
def get_temp_test_data_file() -> Path:
    """Fixture to get test temp data file."""

    return TEMP_TEST_DATA_FILE


@pytest.fixture(scope="session", autouse=True)
def _clean_temp_test_data() -> Generator[None, None, None]:
    """Clean temp test data directory after tests."""
    yield
    rmtree(TEMP_TEST_DATA_DIR)
