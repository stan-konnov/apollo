import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.wilders_swing_index import WildersSwingIndexCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.wilders_swing_index_trend_following import (
    WildersSwingIndexTrendFollowing,
)


@pytest.mark.usefixtures("dataframe", "window_size")
def test__wilders_swing_index_trend_following__with_valid_parameters(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Wilders Swing Index Trend Following with valid parameters.

    Strategy should properly calculate trading signals.
    """

    weighted_tr_multiplier = 0.1

    control_dataframe = dataframe.copy()
    control_dataframe["signal"] = 0

    wsi_calculator = WildersSwingIndexCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
        weighted_tr_multiplier=weighted_tr_multiplier,
    )
    wsi_calculator.calculate_swing_index()

    atr_calculator = AverageTrueRangeCalculator(control_dataframe, window_size)
    atr_calculator.calculate_average_true_range()

    control_dataframe.loc[
        control_dataframe["sp"] == wsi_calculator.HIGH_SWING_POINT,
        "signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        control_dataframe["sp"] == wsi_calculator.LOW_SWING_POINT,
        "signal",
    ] = SHORT_SIGNAL

    control_dataframe.dropna(inplace=True)

    wilders_swing_index_trend_following = WildersSwingIndexTrendFollowing(
        dataframe=dataframe,
        window_size=window_size,
        weighted_tr_multiplier=weighted_tr_multiplier,
    )

    wilders_swing_index_trend_following.model_trading_signals()

    pd.testing.assert_series_equal(dataframe["signal"], control_dataframe["signal"])
