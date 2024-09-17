import pandas as pd
import pytest

from apollo.calculations.engulfing_vix_pattern import (
    EngulfingVIXPatternCalculator,
)
from apollo.settings import LONG_SIGNAL, NO_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base.vix_enhanced_strategy import VIXEnhancedStrategy


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__vix_enhanced_strategy__for_calculating_vix_signals(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test VIX Enhanced Strategy for properly calculating VIX Expansion Contraction.

    Strategy should properly calculate trading signals.
    """

    control_dataframe = enhanced_dataframe.copy()
    control_dataframe["vix_signal"] = NO_SIGNAL

    evp_calculator = EngulfingVIXPatternCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )

    evp_calculator.calculate_engulfing_vix_pattern()

    control_dataframe.loc[
        control_dataframe["vix_ep"] == evp_calculator.BULLISH_ENGULFING,
        "vix_signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        control_dataframe["vix_ep"] == evp_calculator.BEARISH_ENGULFING,
        "vix_signal",
    ] = SHORT_SIGNAL

    VIXEnhancedStrategy(enhanced_dataframe, window_size)

    pd.testing.assert_series_equal(
        control_dataframe["vix_signal"],
        enhanced_dataframe["vix_signal"],
    )
