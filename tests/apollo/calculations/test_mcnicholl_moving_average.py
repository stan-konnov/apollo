import pandas as pd
import pytest

from apollo.calculations.mcnicholl_moving_average import (
    McNichollMovingAverageCalculator,
)


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_mcnicholl_moving_average__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_mcnicholl_moving_average method for correct columns.

    Resulting dataframe must have "mnma" column.
    """

    mnma_calculator = McNichollMovingAverageCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    mnma_calculator.calculate_mcnicholl_moving_average()

    assert "mnma" in mnma_calculator.dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_mcnicholl_moving_average__for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_mcnicholl_moving_average method for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip WINDOW_SIZE - 1 rows for mnma column
    Since McNicholl Moving Average must have at least N rows to be calculated.
    """

    mnma_calculator = McNichollMovingAverageCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    mnma_calculator.calculate_mcnicholl_moving_average()

    assert dataframe["mnma"].isna().sum() == window_size - 1
