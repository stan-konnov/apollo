import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.chaikin_accumulation_distribution import (
    ChaikinAccumulationDistributionCalculator,
)
from apollo.calculations.engulfing_vix_pattern import (
    EngulfingVIXPatternCalculator,
)
from apollo.calculations.hull_moving_average import HullMovingAverageCalculator
from apollo.calculations.keltner_channel import KeltnerChannelCalculator
from apollo.settings import LONG_SIGNAL, NO_SIGNAL, SHORT_SIGNAL
from apollo.strategies.keltner_chaikin_mean_reversion import (
    KeltnerChaikinMeanReversion,
)
from tests.utils.precalculate_shared_values import precalculate_shared_values


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__keltner_chaikin_trend_following__with_valid_parameters(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Keltner Chaikin Trend Following with valid parameters.

    Strategy should properly calculate trading signals.
    """

    enhanced_dataframe = precalculate_shared_values(enhanced_dataframe)

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

    hma_calculator = HullMovingAverageCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    hma_calculator.calculate_hull_moving_average()

    kc_calculator = KeltnerChannelCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
        volatility_multiplier=volatility_multiplier,
    )
    kc_calculator.calculate_keltner_channel()

    cad_calculator = ChaikinAccumulationDistributionCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    cad_calculator.calculate_chaikin_accumulation_distribution_line()

    control_dataframe.loc[
        control_dataframe["vixep"] == evp_calculator.BULLISH_ENGULFING,
        "vix_signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        control_dataframe["vixep"] == evp_calculator.BEARISH_ENGULFING,
        "vix_signal",
    ] = SHORT_SIGNAL

    control_dataframe.loc[
        (control_dataframe["adj close"] < control_dataframe["lkc_bound"])
        & (control_dataframe["adl"] < control_dataframe["prev_adl"])
        | (control_dataframe["vix_signal"] == LONG_SIGNAL),
        "signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        (control_dataframe["adj close"] > control_dataframe["ukc_bound"])
        & (control_dataframe["adl"] > control_dataframe["prev_adl"])
        | (control_dataframe["vix_signal"] == SHORT_SIGNAL),
        "signal",
    ] = SHORT_SIGNAL

    control_dataframe.dropna(inplace=True)

    keltner_chaikin_trend_following = KeltnerChaikinMeanReversion(
        dataframe=enhanced_dataframe,
        window_size=window_size,
        volatility_multiplier=volatility_multiplier,
    )

    keltner_chaikin_trend_following.model_trading_signals()

    pd.testing.assert_series_equal(
        control_dataframe["signal"],
        enhanced_dataframe["signal"],
    )
