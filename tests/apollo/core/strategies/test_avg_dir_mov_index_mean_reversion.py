import pandas as pd
import pytest

from apollo.core.calculations.average_directional_movement_index import (
    AverageDirectionalMovementIndexCalculator,
)
from apollo.core.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.core.calculations.engulfing_vix_pattern import EngulfingVIXPatternCalculator
from apollo.core.strategies.avg_dir_mov_index_mean_reversion import (
    AverageDirectionalMovementIndexMeanReversion,
)
from apollo.settings import LONG_SIGNAL, NO_SIGNAL, SHORT_SIGNAL
from tests.utils.precalculate_shared_values import precalculate_shared_values


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__average_directional_movement_index_mean_reversion__with_valid_parameters(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Average Directional Movement Index Mean Reversion with valid parameters.

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

    adx_calculator = AverageDirectionalMovementIndexCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    adx_calculator.calculate_average_directional_movement_index()

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
            (control_dataframe["adj close"] < control_dataframe["prev_close"])
            & (control_dataframe["dx"] < control_dataframe["prev_dx"])
            & (control_dataframe["dx_adx_ampl"] < control_dataframe["prev_dx_adx_ampl"])
            | (
                (control_dataframe["adj close"] < control_dataframe["prev_close"])
                & (control_dataframe["pdi"] > control_dataframe["prev_pdi"])
                & (control_dataframe["mdi"] > control_dataframe["prev_mdi"])
            )
        )
        | (control_dataframe["vix_signal"] == LONG_SIGNAL),
        "signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        (
            (control_dataframe["adj close"] > control_dataframe["prev_close"])
            & (control_dataframe["dx"] > control_dataframe["prev_dx"])
            & (control_dataframe["dx_adx_ampl"] > control_dataframe["prev_dx_adx_ampl"])
            | (
                (control_dataframe["adj close"] > control_dataframe["prev_close"])
                & (control_dataframe["pdi"] < control_dataframe["prev_pdi"])
                & (control_dataframe["mdi"] < control_dataframe["prev_mdi"])
            )
        )
        | (control_dataframe["vix_signal"] == SHORT_SIGNAL),
        "signal",
    ] = SHORT_SIGNAL

    control_dataframe.dropna(inplace=True)

    avg_dir_mov_index_mean_reversion = AverageDirectionalMovementIndexMeanReversion(
        enhanced_dataframe,
        window_size,
    )

    avg_dir_mov_index_mean_reversion.model_trading_signals()

    pd.testing.assert_series_equal(
        control_dataframe["signal"],
        enhanced_dataframe["signal"],
    )
