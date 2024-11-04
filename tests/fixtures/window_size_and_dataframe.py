from os import curdir
from pathlib import Path

import pandas as pd
import pytest

from apollo.settings import TICKER
from tests.fixtures.files_and_directories import TEST_DIR

WINDOW_SIZE = 5


@pytest.fixture(name="dataframe")
def get_price_dataframe() -> pd.DataFrame:
    """Fixture to get test dataframe from file system."""

    test_dataframe = pd.read_csv(
        Path(f"{Path(curdir).resolve()}/{TEST_DIR}/{TICKER}.csv"),
        index_col=0,
    )
    test_dataframe.index = pd.to_datetime(test_dataframe.index)

    return test_dataframe


@pytest.fixture(name="enhanced_dataframe")
def get_enhanced_price_dataframe() -> pd.DataFrame:
    """Fixture to get enhanced test dataframe from file system."""

    enhanced_test_dataframe = pd.read_csv(
        Path(f"{Path(curdir).resolve()}/{TEST_DIR}/{TICKER}-enhanced.csv"),
        index_col=0,
    )
    enhanced_test_dataframe.index = pd.to_datetime(enhanced_test_dataframe.index)

    return enhanced_test_dataframe


@pytest.fixture(name="screened_tickers_dataframe")
def get_screened_tickers_dataframe() -> pd.DataFrame:
    """Fixture to get screened tickers test dataframe from file system."""

    screened_tickers_test_dataframe = pd.read_csv(
        Path(f"{Path(curdir).resolve()}/{TEST_DIR}/screened-tickers.csv"),
        index_col=0,
    )
    screened_tickers_test_dataframe.index = pd.to_datetime(
        screened_tickers_test_dataframe.index,
    )

    return screened_tickers_test_dataframe


@pytest.fixture(name="window_size", scope="session")
def get_window_size() -> int:
    """Fixture to define window size for calculations."""

    return WINDOW_SIZE


class SameDataframe:
    """
    SameDataframe class.

    Compares two pandas Dataframes using equals method
    to avoid logical comparison operations used by unittest.mock.

    On unit tests argument comparison limitation:
    https://stackoverflow.com/a/69010217/11675550
    """

    def __init__(self, dataframe: pd.DataFrame) -> None:
        """Construct SameDataframe class."""

        self.dataframe = dataframe

    def __eq__(self, other: object) -> bool:
        """Override equals method to compare two pandas Dataframes."""

        return isinstance(other, pd.DataFrame) and other.equals(self.dataframe)


class SameSeries:
    """
    SameSeries class.

    Please see SameDataframe class above.
    """

    def __init__(self, series: pd.Series) -> None:
        """Construct SameSeries class."""

        self.series = series

    def __eq__(self, other: object) -> bool:
        """Override equals method to compare two pandas Series."""

        return isinstance(other, pd.Series) and other.equals(self.series)
