import pandas as pd
import pytest

from apollo.core.calculators.average_true_range import AverageTrueRangeCalculator
from apollo.core.calculators.engulfing_vix_pattern import (
    EngulfingVIXPatternCalculator,
)
from apollo.core.calculators.linear_regression_channel import (
    LinearRegressionChannelCalculator,
)
from apollo.core.strategies.lin_reg_chan_mean_reversion import (
    LinearRegressionChannelMeanReversion,
)
from apollo.settings import LONG_SIGNAL, NO_SIGNAL, SHORT_SIGNAL
from tests.utils.precalculate_shared_values import precalculate_shared_values


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__lin_reg_chan_mean_reversion__with_valid_parameters(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Linear Regression Channel Mean Reversion with valid parameters.

    Strategy should properly calculate trading signals.
    """

    enhanced_dataframe = precalculate_shared_values(enhanced_dataframe)

    channel_sd_spread = 0.5

    control_dataframe = enhanced_dataframe.copy()
    control_dataframe["signal"] = 0
    control_dataframe["vix_signal"] = NO_SIGNAL

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    atr_calculator.calculate_average_true_range()

    evp_calculator = EngulfingVIXPatternCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    evp_calculator.calculate_engulfing_vix_pattern()

    lrc_calculator = LinearRegressionChannelCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
        channel_sd_spread=channel_sd_spread,
    )
    lrc_calculator.calculate_linear_regression_channel()

    control_dataframe.loc[
        control_dataframe["vix_ep"] == evp_calculator.BULLISH_ENGULFING,
        "vix_signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        control_dataframe["vix_ep"] == evp_calculator.BEARISH_ENGULFING,
        "vix_signal",
    ] = SHORT_SIGNAL

    long = (
        (control_dataframe["adj close"] <= control_dataframe["l_bound"])
        & (control_dataframe["slope"] <= control_dataframe["prev_slope"])
    ) | (control_dataframe["vix_signal"] == LONG_SIGNAL)

    control_dataframe.loc[long, "signal"] = LONG_SIGNAL

    short = (
        (control_dataframe["adj close"] >= control_dataframe["u_bound"])
        & (control_dataframe["slope"] >= control_dataframe["prev_slope"])
    ) | (control_dataframe["vix_signal"] == SHORT_SIGNAL)

    control_dataframe.loc[short, "signal"] = SHORT_SIGNAL

    control_dataframe.dropna(inplace=True)

    lin_reg_chan_mean_reversion = LinearRegressionChannelMeanReversion(
        dataframe=enhanced_dataframe,
        window_size=window_size,
        channel_sd_spread=channel_sd_spread,
    )

    lin_reg_chan_mean_reversion.model_trading_signals()

    pd.testing.assert_series_equal(
        control_dataframe["signal"],
        enhanced_dataframe["signal"],
    )
