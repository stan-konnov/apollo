import pandas as pd
import pytest

from apollo.calculators.average_true_range import AverageTrueRangeCalculator
from apollo.calculators.combinatory_futures_patterns import (
    CombinatoryFuturesPatternsCalculator,
)
from apollo.calculators.engulfing_vix_pattern import EngulfingVIXPatternCalculator
from apollo.settings import LONG_SIGNAL, NO_SIGNAL, SHORT_SIGNAL
from apollo.strategies.combinatory_futures_patterns import (
    CombinatoryFuturesPatterns,
)
from tests.utils.precalculate_shared_values import precalculate_shared_values


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__combinatory_futures_patterns__with_valid_parameters(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Combinatory Futures Patterns Strategy with valid parameters.

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

    cfp_calculator = CombinatoryFuturesPatternsCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
        doji_threshold=0.005,
    )
    cfp_calculator.calculate_combinatory_futures_patterns()

    control_dataframe.loc[
        control_dataframe["vix_ep"] == evp_calculator.BULLISH_ENGULFING,
        "vix_signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        control_dataframe["vix_ep"] == evp_calculator.BEARISH_ENGULFING,
        "vix_signal",
    ] = SHORT_SIGNAL

    control_dataframe.loc[
        (
            (control_dataframe["spf_ep"] == cfp_calculator.BEARISH_PATTERN)
            | (
                (control_dataframe["adj close"] < control_dataframe["prev_close"])
                & (control_dataframe["spf_ep_tm1"] == cfp_calculator.BULLISH_PATTERN)
            )
            | (control_dataframe["spf_tp"] == cfp_calculator.BEARISH_PATTERN)
            | (
                (control_dataframe["adj close"] < control_dataframe["prev_close"])
                & (control_dataframe["spf_sp_tm1"] == cfp_calculator.BULLISH_PATTERN)
            )
        )
        | (control_dataframe["vix_signal"] == LONG_SIGNAL),
        "signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        (
            (control_dataframe["spf_ep"] == cfp_calculator.BULLISH_PATTERN)
            | (
                (control_dataframe["adj close"] > control_dataframe["prev_close"])
                & (control_dataframe["spf_ep_tm1"] == cfp_calculator.BEARISH_PATTERN)
            )
            | (control_dataframe["spf_tp"] == cfp_calculator.BULLISH_PATTERN)
            | (
                (control_dataframe["adj close"] > control_dataframe["prev_close"])
                & (control_dataframe["spf_sp_tm1"] == cfp_calculator.BEARISH_PATTERN)
            )
        )
        | (control_dataframe["vix_signal"] == SHORT_SIGNAL),
        "signal",
    ] = SHORT_SIGNAL

    control_dataframe.dropna(inplace=True)

    combinatory_futures_patterns = CombinatoryFuturesPatterns(
        enhanced_dataframe,
        window_size,
        doji_threshold=0.005,
    )

    combinatory_futures_patterns.model_trading_signals()

    pd.testing.assert_series_equal(
        control_dataframe["signal"],
        enhanced_dataframe["signal"],
    )
