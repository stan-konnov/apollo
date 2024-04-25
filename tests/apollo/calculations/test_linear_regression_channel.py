import numpy as np
import pandas as pd
import pytest
from scipy.stats import linregress

from apollo.calculations.linear_regression_channel import (
    LinearRegressionChannelCalculator,
)

CHANNEL_SD_SPREAD = 1.0


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_linear_regression_channel__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_linear_regression_channel method for correct columns.

    Resulting dataframe must have columns "slope", "prev_slope", "l_bound", "u_bound".
    """

    lrc_calculator = LinearRegressionChannelCalculator(
        dataframe=dataframe,
        window_size=window_size,
        channel_sd_spread=CHANNEL_SD_SPREAD,
    )

    lrc_calculator.calculate_linear_regression_channel()

    assert "slope" in dataframe.columns
    assert "prev_slope" in dataframe.columns

    assert "l_bound" in dataframe.columns
    assert "u_bound" in dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_linear_regression_channel__for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_linear_regression_channel method for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip WINDOW_SIZE - 1 rows for each column except
    "prev_slope", since channel calculation must have at least N rows to be calculated.

    Prev slope must skip WINDOW_SIZE rows since it is calculated by shifting "slope".
    """

    ignored_rows_count = window_size - 1

    lrc_calculator = LinearRegressionChannelCalculator(
        dataframe=dataframe,
        window_size=window_size,
        channel_sd_spread=CHANNEL_SD_SPREAD,
    )

    lrc_calculator.calculate_linear_regression_channel()

    assert dataframe["slope"].isna().sum() == ignored_rows_count
    assert dataframe["prev_slope"].isna().sum() == window_size

    assert dataframe["l_bound"].isna().sum() == ignored_rows_count
    assert dataframe["u_bound"].isna().sum() == ignored_rows_count


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_linear_regression_channel__for_correct_indices(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_linear_regression_channel method for correct indices.

    Since channel calculation relies on using numerical indices
    for linear regression, dataframe must be reset before calculation;
    and reset back to date after calculation.

    Resulting dataframe must have "date" as index.
    Resulting dataframe must have "date" as index dtype.
    """

    lrc_calculator = LinearRegressionChannelCalculator(
        dataframe=dataframe,
        window_size=window_size,
        channel_sd_spread=CHANNEL_SD_SPREAD,
    )

    lrc_calculator.calculate_linear_regression_channel()

    assert dataframe.index.name == "date"
    assert dataframe.index.dtype == "datetime64[ns]"


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_linear_regression_channel__for_correct_calculation(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_linear_regression_channel method for correct calculation.

    Resulting dataframe must have correct values for slopes and bounds.
    """

    t_slope = np.full((1, window_size - 1), np.nan).flatten().tolist()
    l_bound = np.full((1, window_size - 1), np.nan).flatten().tolist()
    u_bound = np.full((1, window_size - 1), np.nan).flatten().tolist()

    control_dataframe = dataframe.copy()
    control_dataframe.reset_index(inplace=True)

    control_dataframe["adj close"].rolling(window_size).apply(
        mimic_calc_lin_reg,
        args=(
            t_slope,
            l_bound,
            u_bound,
            CHANNEL_SD_SPREAD,
        ),
    )

    control_dataframe.set_index("date", inplace=True)

    control_dataframe["slope"] = t_slope
    control_dataframe["prev_slope"] = control_dataframe["slope"].shift(1)

    control_dataframe["l_bound"] = l_bound
    control_dataframe["u_bound"] = u_bound

    lrc_calculator = LinearRegressionChannelCalculator(
        dataframe=dataframe,
        window_size=window_size,
        channel_sd_spread=CHANNEL_SD_SPREAD,
    )

    lrc_calculator.calculate_linear_regression_channel()

    pd.testing.assert_series_equal(dataframe["slope"], control_dataframe["slope"])
    pd.testing.assert_series_equal(
        dataframe["prev_slope"],
        control_dataframe["prev_slope"],
    )

    pd.testing.assert_series_equal(dataframe["l_bound"], control_dataframe["l_bound"])
    pd.testing.assert_series_equal(dataframe["u_bound"], control_dataframe["u_bound"])


def mimic_calc_lin_reg(
    series: pd.Series,
    t_slope: list[float],
    l_bound: list[float],
    u_bound: list[float],
    channel_sd_spread: float,
) -> float:
    """
    Mimicry of linear regression calculation for testing purposes.

    Please see LinearRegressionChannelCalculator for
    detailed explanation of linear regression calculation.
    """

    x = series.index
    y = series.to_numpy()

    slope, intercept, _, _, _ = linregress(x, y)

    t_slope.append(slope)

    lbf = slope * x + intercept

    std = y.std()

    lower_bound = lbf - std * channel_sd_spread
    upper_bound = lbf + std * channel_sd_spread

    l_bound.append(lower_bound[-1])
    u_bound.append(upper_bound[-1])

    return 0.0
