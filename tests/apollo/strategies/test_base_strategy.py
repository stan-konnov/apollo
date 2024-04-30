import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.settings import NO_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy


@pytest.mark.usefixtures("dataframe", "window_size")
def test__base_strategy__for_inserting_signal_column(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """Test Base Strategy for inserting "signal" column."""

    strategy = BaseStrategy(dataframe, window_size)

    assert "signal" in strategy.dataframe.columns
    assert strategy.dataframe["signal"].iloc[0] == NO_SIGNAL


@pytest.mark.usefixtures("dataframe", "window_size")
def test__base_strategy__for_calculating_volatility(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """Test Base Strategy for properly calculating volatility (ATR)."""

    control_dataframe = dataframe.copy()

    at_calculator = AverageTrueRangeCalculator(control_dataframe, window_size)
    at_calculator.calculate_average_true_range()

    strategy = BaseStrategy(dataframe, window_size)

    assert "atr" in strategy.dataframe.columns

    pd.testing.assert_series_equal(control_dataframe["atr"], dataframe["atr"])
