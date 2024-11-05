import pandas as pd
import pytest

from apollo.core.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.core.calculations.distribution_moments import DistributionMomentsCalculator
from apollo.core.calculations.engulfing_vix_pattern import (
    EngulfingVIXPatternCalculator,
)
from apollo.core.strategies.skew_kurt_vol_trend_following import (
    SkewnessKurtosisVolatilityTrendFollowing,
)
from apollo.settings import LONG_SIGNAL, NO_SIGNAL, SHORT_SIGNAL
from tests.utils.precalculate_shared_values import precalculate_shared_values


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__skew_kurt_vol_trend_following__with_valid_parameters(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Skewness Kurtosis Volatility Trend Following with valid parameters.

    Strategy should properly calculate trading signals.
    """

    enhanced_dataframe = precalculate_shared_values(enhanced_dataframe)

    kurtosis_threshold = 0.0
    volatility_multiplier = 0.5

    control_dataframe = enhanced_dataframe.copy()
    control_dataframe["signal"] = NO_SIGNAL
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

    dm_calculator = DistributionMomentsCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    dm_calculator.calculate_distribution_moments()

    control_dataframe.loc[
        control_dataframe["vix_ep"] == evp_calculator.BULLISH_ENGULFING,
        "vix_signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        control_dataframe["vix_ep"] == evp_calculator.BEARISH_ENGULFING,
        "vix_signal",
    ] = SHORT_SIGNAL

    long = (
        (control_dataframe["skew"] < 0)
        & (control_dataframe["kurt"] < kurtosis_threshold)
        & (control_dataframe["tr"] > control_dataframe["atr"] * volatility_multiplier)
    ) | (control_dataframe["vix_signal"] == LONG_SIGNAL)

    control_dataframe.loc[long, "signal"] = LONG_SIGNAL

    short = (
        (control_dataframe["skew"] > 0)
        & (control_dataframe["kurt"] < kurtosis_threshold)
        & (control_dataframe["tr"] > control_dataframe["atr"] * volatility_multiplier)
    ) | (control_dataframe["vix_signal"] == SHORT_SIGNAL)

    control_dataframe.loc[short, "signal"] = SHORT_SIGNAL

    control_dataframe.dropna(inplace=True)

    skew_kurt_vol_trend_following = SkewnessKurtosisVolatilityTrendFollowing(
        dataframe=enhanced_dataframe,
        window_size=window_size,
        kurtosis_threshold=kurtosis_threshold,
        volatility_multiplier=volatility_multiplier,
    )

    skew_kurt_vol_trend_following.model_trading_signals()

    pd.testing.assert_series_equal(
        control_dataframe["signal"],
        enhanced_dataframe["signal"],
    )
