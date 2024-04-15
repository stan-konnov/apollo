import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator


@pytest.mark.usefixtures("dataframe")
@pytest.mark.usefixtures("window_size")
def test__calculate_average_true_range__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_average_true_range method for correct columns.

    Resulting dataframe must have columns "tr" and "atr".
    """

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    atr_calculator.calculate_average_true_range()

    assert "tr" in atr_calculator.dataframe.columns
    assert "atr" in atr_calculator.dataframe.columns


@pytest.mark.usefixtures("dataframe")
@pytest.mark.usefixtures("window_size")
def test__calculate_average_true_range__for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
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
        dataframe=dataframe,
        window_size=window_size,
    )

    atr_calculator.calculate_average_true_range()

    assert dataframe["tr"].isna().sum() == window_size - 1
    assert dataframe["atr"].isna().sum() == (window_size - 1) * 2

