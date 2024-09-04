import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.conners_vix_expansion_contraction import (
    EngulfingVIXPatternCalculator,
)
from apollo.calculations.linear_regression_channel import (
    LinearRegressionChannelCalculator,
)
from apollo.settings import LONG_SIGNAL, NO_SIGNAL, SHORT_SIGNAL
from apollo.strategies.lin_reg_chan_mean_reversion import (
    LinearRegressionChannelMeanReversion,
)


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__lin_reg_chan_mean_reversion__with_valid_parameters(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Linear Regression Channel Mean Reversion with valid parameters.

    Strategy should properly calculate trading signals.
    """

    channel_sd_spread = 0.5

    control_dataframe = enhanced_dataframe.copy()
    control_dataframe["signal"] = 0
    control_dataframe["vix_signal"] = NO_SIGNAL

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    atr_calculator.calculate_average_true_range()

    cvec_calculator = EngulfingVIXPatternCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    cvec_calculator.calculate_vix_expansion_contraction()

    lrc_calculator = LinearRegressionChannelCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
        channel_sd_spread=channel_sd_spread,
    )
    lrc_calculator.calculate_linear_regression_channel()

    control_dataframe.loc[
        control_dataframe["cvec"] == cvec_calculator.UPSIDE_EXPANSION,
        "vix_signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        control_dataframe["cvec"] == cvec_calculator.DOWNSIDE_CONTRACTION,
        "vix_signal",
    ] = SHORT_SIGNAL

    long = (control_dataframe["adj close"] <= control_dataframe["l_bound"]) & (
        control_dataframe["slope"] <= control_dataframe["prev_slope"]
    ) | (control_dataframe["vix_signal"] == LONG_SIGNAL)

    control_dataframe.loc[long, "signal"] = LONG_SIGNAL

    short = (control_dataframe["adj close"] >= control_dataframe["u_bound"]) & (
        control_dataframe["slope"] >= control_dataframe["prev_slope"]
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
