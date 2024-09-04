import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.distribution_moments import DistributionMomentsCalculator
from apollo.calculations.engulfing_vix_pattern import (
    EngulfingVIXPatternCalculator,
)
from apollo.settings import LONG_SIGNAL, NO_SIGNAL, SHORT_SIGNAL
from apollo.strategies.skew_kurt_vol_trend_following import (
    SkewnessKurtosisVolatilityTrendFollowing,
)


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__skew_kurt_vol_trend_following__with_valid_parameters(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Skewness Kurtosis Volatility Trend Following with valid parameters.

    Strategy should properly calculate trading signals.
    """

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

    cvec_calculator = EngulfingVIXPatternCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    cvec_calculator.calculate_vix_expansion_contraction()

    dm_calculator = DistributionMomentsCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    dm_calculator.calculate_distribution_moments()

    control_dataframe.loc[
        control_dataframe["cvec"] == cvec_calculator.UPSIDE_EXPANSION,
        "vix_signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        control_dataframe["cvec"] == cvec_calculator.DOWNSIDE_CONTRACTION,
        "vix_signal",
    ] = SHORT_SIGNAL

    long = (control_dataframe["skew"] < 0) & (
        control_dataframe["kurt"] < kurtosis_threshold
    ) & (control_dataframe["tr"] > control_dataframe["atr"] * volatility_multiplier) | (
        control_dataframe["vix_signal"] == LONG_SIGNAL
    )

    control_dataframe.loc[long, "signal"] = LONG_SIGNAL

    short = (control_dataframe["skew"] > 0) & (
        control_dataframe["kurt"] < kurtosis_threshold
    ) & (control_dataframe["tr"] > control_dataframe["atr"] * volatility_multiplier) | (
        control_dataframe["vix_signal"] == SHORT_SIGNAL
    )

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
