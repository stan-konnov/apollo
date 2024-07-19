from os import curdir
from pathlib import Path
from shutil import rmtree
from typing import Generator

import pytest

TEMP_TEST_DIR = Path(f"{Path(curdir).resolve()}/tests/temp")
PLOT_DIR = Path(f"{TEMP_TEST_DIR}/backtesting_plots")
TEST_DIR = "tests/test_data"


@pytest.fixture(scope="session", autouse=True)
def _clean_data() -> Generator[None, None, None]:
    """Clean temp test data directory after tests."""
    yield
    rmtree(TEMP_TEST_DIR)
