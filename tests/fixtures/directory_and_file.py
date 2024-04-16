from os import curdir
from pathlib import Path
from shutil import rmtree
from typing import Generator
from unittest.mock import patch

import pytest

from apollo.settings import (
    END_DATE,
    START_DATE,
    STRATEGY,
    TICKER,
    ValidYahooApiFrequencies,
)

TEMP_DIR = Path(f"{Path(curdir).resolve()}/tests/temp")
PARM_FIL = Path(f"{TEMP_DIR}/{STRATEGY}.json")
DATA_FIL = Path(
    str(
        f"{TEMP_DIR}/{TICKER}-"
        f"{ValidYahooApiFrequencies.ONE_DAY.value}-"
        f"{START_DATE}-{END_DATE}.csv",
    ),
)

@pytest.fixture(name="data_dir", scope="session")
def _get_data_dir() -> Generator[None, None, None]:
    """Fixture to get data directory for testing Yahoo API Connector."""

    with patch("apollo.api.yahoo_api_connector.DATA_DIR", TEMP_DIR):
        yield


@pytest.fixture(name="data_file", scope="session")
def get_data_file() -> Path:
    """Fixture to get data file."""

    return DATA_FIL


@pytest.fixture(name="parameters_dir", scope="session")
def _get_parameters_dir() -> Generator[None, None, None]:
    """Fixture to get parameters directory for testing Configuration."""

    with patch("apollo.utils.configuration.PARM_DIR", TEMP_DIR):
        yield


@pytest.fixture(name="parameters_file", scope="session")
def get_parameters_file() -> Path:
    """Fixture to get parameters file."""

    return PARM_FIL


@pytest.fixture(scope="session", autouse=True)
def _clean_data() -> Generator[None, None, None]:
    """Clean temp test data directory after tests."""

    yield
    rmtree(TEMP_DIR)
