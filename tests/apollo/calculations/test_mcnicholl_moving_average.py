import pandas as pd
import pytest

from apollo.calculations.hull_moving_average import (
    HullMovingAverageCalculator,
)


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_hull_moving_average__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_hull_moving_average method for correct columns.

    Resulting dataframe must have "hma" column.
    """

    hma_calculator = HullMovingAverageCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    hma_calculator.calculate_hull_moving_average()

    assert "hma" in hma_calculator.dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_hull_moving_average__for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_hull_moving_average method for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip WINDOW_SIZE - 1 rows for hma column
    Since McNicholl Moving Average must have at least N rows to be calculated.
    """

    hma_calculator = HullMovingAverageCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    hma_calculator.calculate_hull_moving_average()

    assert dataframe["hma"].isna().sum() == window_size - 1


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_hull_moving_average__for_correct_hma_calculation(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_hull_moving_average method for correct calculation.

    Resulting "hma" column must have correct values for each row.
    """

    control_dataframe = dataframe.copy()

    smoothing_factor = 2 / (window_size + 1)

    simple_moving_average = (
        control_dataframe["adj close"]
        .rolling(window=window_size, min_periods=window_size)
        .mean()
    )

    weights = (1 - smoothing_factor) ** pd.Series(
        len(dataframe.index),
        index=dataframe.index,
    )

    weights = weights[::-1]

    weighted_close = control_dataframe["adj close"] * smoothing_factor * weights

    close_cumulative_sum = weighted_close[::-1].expanding().sum()[::-1]

    weights_cumulative_sum = weights.expanding().sum()[::-1]

    mcnicholl_ma = close_cumulative_sum / weights_cumulative_sum

    mcnicholl_ma[:window_size] = simple_moving_average[:window_size]

    control_dataframe["hma"] = mcnicholl_ma

    hma_calculator = HullMovingAverageCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    hma_calculator.calculate_hull_moving_average()

    pd.testing.assert_series_equal(dataframe["hma"], control_dataframe["hma"])
