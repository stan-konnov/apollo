import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.distribution_moments import DistributionMomentsCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.skew_kurt_vol_trend_following import (
    SkewnessKurtosisVolatilityTrendFollowing,
)


@pytest.mark.usefixtures("dataframe", "window_size")
def test__skew_kurt_vol_trend_following__with_valid_parameters(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Skewness Kurtosis Volatility Trend Following with valid parameters.

    Strategy should properly calculate trading signals.
    """

    kurtosis_threshold = 0.0
    volatility_multiplier = 0.5

    control_dataframe = dataframe.copy()
    control_dataframe["signal"] = 0

    dm_calculator = DistributionMomentsCalculator(control_dataframe, window_size)
    dm_calculator.calculate_distribution_moments()

    atr_calculator = AverageTrueRangeCalculator(control_dataframe, window_size)
    atr_calculator.calculate_average_true_range()

    long = (
        (control_dataframe["skew"] < 0)
        & (control_dataframe["kurt"] < kurtosis_threshold)
        & (control_dataframe["tr"] > control_dataframe["atr"] * volatility_multiplier)
    )
    control_dataframe.loc[long, "signal"] = LONG_SIGNAL

    short = (
        (control_dataframe["skew"] > 0)
        & (control_dataframe["kurt"] < kurtosis_threshold)
        & (control_dataframe["tr"] > control_dataframe["atr"] * volatility_multiplier)
    )
    control_dataframe.loc[short, "signal"] = SHORT_SIGNAL

    control_dataframe.dropna(inplace=True)

    skew_kurt_vol_trend_following = SkewnessKurtosisVolatilityTrendFollowing(
        dataframe=dataframe,
        window_size=window_size,
        kurtosis_threshold=kurtosis_threshold,
        volatility_multiplier=volatility_multiplier,
    )

    skew_kurt_vol_trend_following.model_trading_signals()

    pd.testing.assert_series_equal(dataframe["signal"], control_dataframe["signal"])
