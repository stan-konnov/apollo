import pandas as pd
import pytest

from apollo.core.calculators.average_true_range import AverageTrueRangeCalculator
from apollo.core.calculators.swing_events import SwingEventsCalculator
from apollo.core.strategies.swing_events_mean_reversion import SwingEventsMeanReversion
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from tests.utils.precalculate_shared_values import precalculate_shared_values


@pytest.mark.usefixtures("dataframe", "window_size")
def test__swing_events_mean_reversion__with_valid_parameters(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Swing Events Mean Reversion with valid parameters.

    Strategy should properly calculate trading signals.
    """

    dataframe = precalculate_shared_values(dataframe)

    swing_filter = 0.01

    control_dataframe = dataframe.copy()
    control_dataframe["signal"] = 0

    se_calculator = SwingEventsCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
        swing_filter=swing_filter,
    )
    se_calculator.calculate_swing_events()

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    atr_calculator.calculate_average_true_range()

    control_dataframe.loc[
        control_dataframe["se"] == se_calculator.DOWN_SWING,
        "signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        control_dataframe["se"] == se_calculator.UP_SWING,
        "signal",
    ] = SHORT_SIGNAL

    control_dataframe.dropna(inplace=True)

    swing_events_mean_reversion = SwingEventsMeanReversion(
        dataframe=dataframe,
        window_size=window_size,
        swing_filter=swing_filter,
    )

    swing_events_mean_reversion.model_trading_signals()

    pd.testing.assert_series_equal(dataframe["signal"], control_dataframe["signal"])
