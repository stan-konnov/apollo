import pandas as pd
import pytest

from apollo.calculations.swing_moments import SwingMomentsCalculator

SWING_FILTER = 0.03


@pytest.mark.usefixtures("dataframe")
@pytest.mark.usefixtures("window_size")
def test__calculate_swing_moments__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_swing_moments method for correct columns.

    Resulting dataframe must have "sm" column.
    """

    sm_calculator = SwingMomentsCalculator(
        dataframe=dataframe,
        window_size=window_size,
        swing_filter=SWING_FILTER,
    )

    sm_calculator.calculate_swing_moments()

    assert "sm" in dataframe.columns


@pytest.mark.usefixtures("dataframe")
@pytest.mark.usefixtures("window_size")
def test__calculate_swing_moments__for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_swing_moments method for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip WINDOW_SIZE - 1 rows for SM column
    Since SM calculation must have at least N rows to be calculated.
    """

    sm_calculator = SwingMomentsCalculator(
        dataframe=dataframe,
        window_size=window_size,
        swing_filter=SWING_FILTER,
    )

    sm_calculator.calculate_swing_moments()

    assert dataframe["sm"].isna().sum() == window_size - 1
