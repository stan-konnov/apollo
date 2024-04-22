from os import curdir
from pathlib import Path
from shutil import rmtree
from typing import Generator

import pytest

from apollo.settings import (
    ValidYahooApiFrequencies,
)
from tests.fixtures.env_and_constants import (
    END_DATE,
    START_DATE,
    STRATEGY,
    TICKER,
)

TEMP_TEST_DIR = Path(f"{Path(curdir).resolve()}/tests/temp")

DATA_DIR = Path(f"{TEMP_TEST_DIR}/data")

DATA_FILE = Path(
    str(
        f"{DATA_DIR}/{TICKER}-"
        f"{ValidYahooApiFrequencies.ONE_DAY.value}-"
        f"{START_DATE}-{END_DATE}.csv",
    ),
)

PLOT_DIR = Path(f"{TEMP_TEST_DIR}/backtesting_plots")

TEST_DIR = "tests/test_data"

PARM_DIR = TEST_DIR

PARM_FILE_PATH = f"{PARM_DIR}/{STRATEGY}.json"

BRES_DIR = Path(f"{TEMP_TEST_DIR}/backtesting_results")

OPTP_DIR = Path(f"{TEMP_TEST_DIR}/parameters_opt")


@pytest.fixture(scope="session", autouse=True)
def _clean_data() -> Generator[None, None, None]:
    """Clean temp test data directory after tests."""
    yield
    rmtree(TEMP_TEST_DIR)
