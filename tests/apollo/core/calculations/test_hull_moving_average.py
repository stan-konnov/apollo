import numpy as np
import pandas as pd
import pytest

from apollo.core.calculators.hull_moving_average import (
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

    assert "hma" in dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_hull_moving_average__for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_hull_moving_average method for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must equal to N, since Hull Moving Average
    is calculated on top of weighted moving average that requires
    exactly N elements to calculate the weights for the window.
    """

    hma_calculator = HullMovingAverageCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    hma_calculator.calculate_hull_moving_average()

    assert dataframe["hma"].isna().sum() == window_size


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

    standard_window_wma = _calc_wma(
        control_dataframe["adj close"],
        window_size,
    )

    half_window = window_size // 2

    half_window_wma = _calc_wma(
        control_dataframe["adj close"],
        half_window,
    )

    wma_difference = 2 * half_window_wma - standard_window_wma

    sqrt_window = int(np.sqrt(window_size))

    hull_moving_average = _calc_wma(
        wma_difference,
        sqrt_window,
    )

    # Write to the dataframe
    control_dataframe["hma"] = hull_moving_average

    hma_calculator = HullMovingAverageCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    hma_calculator.calculate_hull_moving_average()

    pd.testing.assert_series_equal(dataframe["hma"], control_dataframe["hma"])


def _calc_wma(
    series: pd.Series,
    window_size: int,
) -> pd.Series:
    """
    Mimicry of Weighted Moving Average calculation for testing purposes.

    Please see HullMovingAverageCalculator for
    detailed explanation of Weighted Moving Average calculation.
    """

    weights = np.arange(1, window_size + 1)

    return series.rolling(window=window_size).apply(
        lambda x: np.sum(x * weights) / np.sum(weights),
        raw=True,
    )
