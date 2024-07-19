from os import curdir
from pathlib import Path

import pandas as pd
import pytest

from tests.fixtures.env_and_constants import TICKER
from tests.fixtures.files_and_directories import TEST_DIR

WINDOW_SIZE = 5


@pytest.fixture(name="dataframe", scope="module")
def get_price_dataframe() -> pd.DataFrame:
    """Fixture to get test dataframe from file system."""

    test_dataframe = pd.read_csv(
        Path(f"{Path(curdir).resolve()}/{TEST_DIR}/{TICKER}.csv"),
        index_col=0,
    )
    test_dataframe.index = pd.to_datetime(test_dataframe.index)

    return test_dataframe


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
