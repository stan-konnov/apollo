import pandas as pd
import pytest

from apollo.calculations.wilders_swing_index import WildersSwingIndexCalculator


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_swing_index__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_swing_index method for correct columns.

    Resulting dataframe must have "sp" column.
    """

    wsi_calculator = WildersSwingIndexCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    wsi_calculator.calculate_swing_index()

    assert "sp" in dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_swing_index__for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_swing_index method for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip WINDOW_SIZE rows for SP column
    Since SP calculation relies on 3 consecutive ASI values,
    and, in such, only available after first N rows.
    """

    wsi_calculator = WildersSwingIndexCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    wsi_calculator.calculate_swing_index()

    assert dataframe["sp"].isna().sum() == window_size
