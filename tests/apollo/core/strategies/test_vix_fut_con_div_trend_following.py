import pandas as pd
import pytest

from apollo.core.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.core.calculations.vix_futures_convergence_divergence import (
    VIXFuturesConvergenceDivergenceCalculator,
)
from apollo.core.strategies.vix_fut_con_div_trend_following import (
    VIXFuturesConvergenceDivergenceTrendFollowing,
)
from apollo.settings import LONG_SIGNAL, NO_SIGNAL, SHORT_SIGNAL
from tests.utils.precalculate_shared_values import precalculate_shared_values


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__vix_fut_con_div_trend_following__with_valid_parameters(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test VIx Future Convergence Divergence Trend Following with valid parameters.

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

    vfcd_calculator = VIXFuturesConvergenceDivergenceCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    vfcd_calculator.calculate_vix_futures_convergence_divergence()

    control_dataframe.loc[
        (control_dataframe["adj close"] > control_dataframe["prev_close"])
        & (
            control_dataframe["vix_spf_pct_diff"]
            < control_dataframe["prev_vix_spf_pct_diff"]
        ),
        "signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        (control_dataframe["adj close"] < control_dataframe["prev_close"])
        & (
            control_dataframe["vix_spf_pct_diff"]
            > control_dataframe["prev_vix_spf_pct_diff"]
        ),
        "signal",
    ] = SHORT_SIGNAL

    control_dataframe.dropna(inplace=True)

    vix_fut_con_div_mean_reversion = VIXFuturesConvergenceDivergenceTrendFollowing(
        enhanced_dataframe,
        window_size,
    )

    vix_fut_con_div_mean_reversion.model_trading_signals()

    pd.testing.assert_series_equal(
        control_dataframe["signal"],
        enhanced_dataframe["signal"],
    )
