import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.engulfing_vix_pattern import (
    EngulfingVIXPatternCalculator,
)
from apollo.settings import LONG_SIGNAL, NO_SIGNAL, SHORT_SIGNAL
from apollo.strategies.engulfing_vix_mean_reversion import (
    EngulfingVIXMeanReversion,
)


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__vix_exp_con_mean_reversion__with_valid_parameters(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test VIX Expansion Contraction Mean Reversion Strategy with valid parameters.

    Strategy should properly calculate trading signals.
    """

    control_dataframe = enhanced_dataframe.copy()
    control_dataframe["signal"] = NO_SIGNAL

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

    control_dataframe.loc[
        control_dataframe["cvec"] == cvec_calculator.UPSIDE_EXPANSION,
        "signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        control_dataframe["cvec"] == cvec_calculator.DOWNSIDE_CONTRACTION,
        "signal",
    ] = SHORT_SIGNAL

    control_dataframe.dropna(inplace=True)

    vix_exp_con_mean_reversion = EngulfingVIXMeanReversion(
        enhanced_dataframe,
        window_size,
    )

    vix_exp_con_mean_reversion.model_trading_signals()

    pd.testing.assert_series_equal(
        control_dataframe["signal"],
        enhanced_dataframe["signal"],
    )
