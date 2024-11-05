import pandas as pd
import pytest

from apollo.core.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.core.calculations.engulfing_vix_pattern import (
    EngulfingVIXPatternCalculator,
)
from apollo.core.strategies.engulfing_vix_mean_reversion import (
    EngulfingVIXMeanReversion,
)
from apollo.settings import LONG_SIGNAL, NO_SIGNAL, SHORT_SIGNAL
from tests.utils.precalculate_shared_values import precalculate_shared_values


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__engulfing_vix_mean_reversion__with_valid_parameters(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Engulfing VIX Mean Reversion Strategy with valid parameters.

    Strategy should properly calculate trading signals.
    """

    enhanced_dataframe = precalculate_shared_values(enhanced_dataframe)

    control_dataframe = enhanced_dataframe.copy()
    control_dataframe["signal"] = NO_SIGNAL

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

    control_dataframe.loc[
        control_dataframe["vix_ep"] == evp_calculator.BULLISH_ENGULFING,
        "signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        control_dataframe["vix_ep"] == evp_calculator.BEARISH_ENGULFING,
        "signal",
    ] = SHORT_SIGNAL

    control_dataframe.dropna(inplace=True)

    engulfing_vix_mean_reversion = EngulfingVIXMeanReversion(
        enhanced_dataframe,
        window_size,
    )

    engulfing_vix_mean_reversion.model_trading_signals()

    pd.testing.assert_series_equal(
        control_dataframe["signal"],
        enhanced_dataframe["signal"],
    )
