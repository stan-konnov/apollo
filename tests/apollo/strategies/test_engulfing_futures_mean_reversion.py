import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.engulfing_futures_pattern import (
    EngulfingFuturesPatternCalculator,
)
from apollo.calculations.engulfing_vix_pattern import EngulfingVIXPatternCalculator
from apollo.settings import LONG_SIGNAL, NO_SIGNAL, SHORT_SIGNAL
from apollo.strategies.engulfing_futures_mean_reversion import (
    EngulfingFuturesMeanReversion,
)
from tests.utils.precalculate_shared_values import precalculate_shared_values


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__engulfing_futures_mean_reversion__with_valid_parameters(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Engulfing Futures Mean Reversion Strategy with valid parameters.

    Strategy should properly calculate trading signals.
    """

    enhanced_dataframe = precalculate_shared_values(enhanced_dataframe)

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

    efp_calculator = EngulfingFuturesPatternCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )

    efp_calculator.calculate_engulfing_futures_pattern()

    control_dataframe.loc[
        control_dataframe["vixep"] == evp_calculator.BULLISH_ENGULFING,
        "vix_signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        control_dataframe["vixep"] == evp_calculator.BEARISH_ENGULFING,
        "vix_signal",
    ] = SHORT_SIGNAL

    control_dataframe.loc[
        (
            (control_dataframe["spfep"] == efp_calculator.BEARISH_ENGULFING)
            | (control_dataframe["vix_signal"] == LONG_SIGNAL)
        ),
        "signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        (
            (control_dataframe["spfep"] == efp_calculator.BULLISH_ENGULFING)
            | (control_dataframe["vix_signal"] == SHORT_SIGNAL)
        ),
        "signal",
    ] = SHORT_SIGNAL

    control_dataframe.dropna(inplace=True)

    engulfing_futures_mean_reversion = EngulfingFuturesMeanReversion(
        enhanced_dataframe,
        window_size,
    )

    engulfing_futures_mean_reversion.model_trading_signals()

    pd.testing.assert_series_equal(
        control_dataframe["signal"],
        enhanced_dataframe["signal"],
    )
