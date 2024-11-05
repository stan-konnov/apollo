import pandas as pd
import pytest

from apollo.core.calculators.kaufman_efficiency_ratio import (
    KaufmanEfficiencyRatioCalculator,
)


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_kaufman_efficiency_ratio__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_kaufman_efficiency_ratio method for correct columns.

    Resulting dataframe must have "ker" column.
    """
    ker_calculator = KaufmanEfficiencyRatioCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    ker_calculator.calculate_kaufman_efficiency_ratio()

    assert "ker" in dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_kaufman_efficiency_ratio_for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_kaufman_efficiency_ratio method for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip WINDOW_SIZE rows for ker column
    Since KER calculation relies on prices from one window back.
    """
    ker_calculator = KaufmanEfficiencyRatioCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    ker_calculator.calculate_kaufman_efficiency_ratio()

    assert dataframe["ker"].isna().sum() == window_size


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_kaufman_efficiency_ratio__for_correct_ker_calculation(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_kaufman_efficiency_ratio method for correct Kaufman Efficiency Ratio.

    Resulting "ker" column must have correct values for each row.
    """

    control_dataframe = dataframe.copy()

    close_one_window_back = control_dataframe["adj close"].shift(
        window_size,
    )

    abs_price_differ = (control_dataframe["adj close"] - close_one_window_back).abs()

    abs_price_change = control_dataframe["adj close"].diff().abs()

    abs_price_change_sum = abs_price_change.rolling(
        window=window_size,
        min_periods=window_size,
    ).sum()

    control_dataframe["ker"] = abs_price_differ / abs_price_change_sum

    ker_calculator = KaufmanEfficiencyRatioCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    ker_calculator.calculate_kaufman_efficiency_ratio()

    pd.testing.assert_series_equal(dataframe["ker"], control_dataframe["ker"])
