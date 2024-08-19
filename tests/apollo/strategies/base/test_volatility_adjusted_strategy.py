import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.strategies.base.volatility_adjusted_strategy import (
    VolatilityAdjustedStrategy,
)


@pytest.mark.usefixtures("dataframe", "window_size")
def test__volatility_adjusted_strategy__for_calculating_volatility(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Volatility Adjusted Strategy for properly calculating volatility (ATR).

    Strategy should have "tr" and "atr" columns.
    """

    control_dataframe = dataframe.copy()

    at_calculator = AverageTrueRangeCalculator(control_dataframe, window_size)
    at_calculator.calculate_average_true_range()

    VolatilityAdjustedStrategy(dataframe, window_size)

    assert "tr" in dataframe.columns
    assert "atr" in dataframe.columns
    pd.testing.assert_series_equal(control_dataframe["atr"], dataframe["atr"])
