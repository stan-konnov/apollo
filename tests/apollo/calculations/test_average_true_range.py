from os import curdir
from pathlib import Path

import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator

WINDOW_SIZE = 5


@pytest.fixture(name="test_dataframe")
def get_price_dataframe() -> pd.DataFrame:
    """Fixture to get test dataframe from file system."""

    test_dataframe = pd.read_csv(
        Path(f"{Path(curdir).resolve()}/tests/data/test.csv"),
        index_col=0,
    )

    test_dataframe.index = pd.to_datetime(test_dataframe.index)

    return test_dataframe


@pytest.mark.usefixtures("test_dataframe")
def test__calculate_average_true_range__for_correct_columns(
    test_dataframe: pd.DataFrame,
) -> None:
    """
    Test calculate_average_true_range method for correct columns.

    Resulting dataframe must have columns "tr" and "atr".
    """

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=test_dataframe,
        window_size=WINDOW_SIZE,
    )

    atr_calculator.calculate_average_true_range()

    assert "tr" in atr_calculator.dataframe.columns
    assert "atr" in atr_calculator.dataframe.columns


@pytest.mark.usefixtures("test_dataframe")
def test__calculate_average_true_range__for_correct_rolling_window(
    test_dataframe: pd.DataFrame,
) -> None:
    """
    Test calculate_average_true_range method for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip WINDOW_SIZE - 1 rows for TR column
    Since TR calculation must have at least N rows to calculate TR.

    Resulting dataframe must skip (WINDOW_SIZE - 1) * 2 rows for ATR column
    Since ATR calculation must have at least N rows of valid TR to calculate ATR.
    """

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=test_dataframe,
        window_size=WINDOW_SIZE,
    )

    atr_calculator.calculate_average_true_range()

    assert test_dataframe["tr"].isna().sum() == WINDOW_SIZE - 1
    assert test_dataframe["atr"].isna().sum() == (WINDOW_SIZE - 1) * 2

