import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.swing_events import SwingEventsCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.swing_events_mean_reversion import SwingEventsMeanReversion


@pytest.mark.usefixtures("dataframe", "window_size")
def test__swing_events_mean_reversion__with_valid_parameters(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Swing Events Mean Reversion with valid parameters.

    Strategy should have relevant columns: "signal", "se".

    Strategy should properly calculate trading signals.
    """

    swing_filter = 0.01

    control_dataframe = dataframe.copy()
    control_dataframe["signal"] = 0

    se_calculator = SwingEventsCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
        swing_filter=swing_filter,
    )
    se_calculator.calculate_swing_events()

    atr_calculator = AverageTrueRangeCalculator(control_dataframe, window_size)
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

    assert "signal" in swing_events_mean_reversion.dataframe.columns
    assert "se" in swing_events_mean_reversion.dataframe.columns

    pd.testing.assert_series_equal(dataframe["signal"], control_dataframe["signal"])
