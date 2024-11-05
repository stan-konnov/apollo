import pandas as pd
import pytest

from apollo.core.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.core.calculations.elliot_waves import ElliotWavesCalculator
from apollo.core.strategies.combinatory_elliot_waves import CombinatoryElliotWaves
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from tests.utils.precalculate_shared_values import precalculate_shared_values


@pytest.mark.usefixtures("dataframe", "window_size")
def test__combinatory_elliot_waves__with_valid_parameters(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Combinatory Elliot Waves with valid parameters.

    Strategy should properly calculate trading signals.
    """

    dataframe = precalculate_shared_values(dataframe)

    fast_oscillator_period = 5.0
    slow_oscillator_period = 10.0

    control_dataframe = dataframe.copy()
    control_dataframe["signal"] = 0

    ew_calculator = ElliotWavesCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
        fast_oscillator_period=fast_oscillator_period,
        slow_oscillator_period=slow_oscillator_period,
    )
    ew_calculator.calculate_elliot_waves()

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    atr_calculator.calculate_average_true_range()

    control_dataframe.loc[
        control_dataframe["ew"] == ew_calculator.UPWARD_WAVE,
        "signal",
    ] = LONG_SIGNAL

    control_dataframe.loc[
        control_dataframe["ew"] == ew_calculator.DOWNWARD_WAVE,
        "signal",
    ] = SHORT_SIGNAL

    control_dataframe.dropna(inplace=True)

    swing_events_mean_reversion = CombinatoryElliotWaves(
        dataframe=dataframe,
        window_size=window_size,
        fast_oscillator_period=fast_oscillator_period,
        slow_oscillator_period=slow_oscillator_period,
    )

    swing_events_mean_reversion.model_trading_signals()

    pd.testing.assert_series_equal(dataframe["signal"], control_dataframe["signal"])
