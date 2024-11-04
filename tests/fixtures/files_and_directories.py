from os import curdir
from pathlib import Path
from shutil import rmtree
from typing import Generator

import pytest

TEMP_TEST_DIR = Path(f"{Path(curdir).resolve()}/tests/temp")
PLOT_DIR = Path(f"{TEMP_TEST_DIR}/backtesting_plots")
TRDS_DIR = Path(f"{TEMP_TEST_DIR}/backtesting_trades")
TEST_DIR = "tests/test_data"


@pytest.fixture(name="clean_data")
def _clean_data() -> Generator[None, None, None]:
    """Clean temp test data directory after tests."""
    yield
    rmtree(TEMP_TEST_DIR)


@pytest.fixture(name="sp500_components_page")
def get_sp500_components_page() -> str:
    """Return S&P 500 components page HTML."""

    with Path.open(
        Path(f"{TEST_DIR}/sp500-components-page.html"),
    ) as sp500_components_page_file:
        return sp500_components_page_file.read()
