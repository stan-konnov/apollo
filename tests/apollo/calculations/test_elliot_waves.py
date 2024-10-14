import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.elliot_waves import ElliotWavesCalculator
from tests.utils.precalculate_shared_values import precalculate_shared_values

FAST_OSCILLATOR_PERIOD = 5
SLOW_OSCILLATOR_PERIOD = 10


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_elliot_waves__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_elliot_waves method for correct columns.

    Resulting dataframe must have "ew" column.

    Resulting dataframe must not have the following columns:
    "ewo", "ewo_sma", "slow_hla_sma", "fast_hla_sma", "high_low_avg".
    """

    dataframe = precalculate_shared_values(dataframe)

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    atr_calculator.calculate_average_true_range()

    ew_calculator = ElliotWavesCalculator(
        dataframe=dataframe,
        window_size=window_size,
        fast_oscillator_period=FAST_OSCILLATOR_PERIOD,
        slow_oscillator_period=SLOW_OSCILLATOR_PERIOD,
    )
    ew_calculator.calculate_elliot_waves()

    assert "ew" in dataframe.columns

    assert "ewo" not in dataframe.columns
    assert "ewo_sma" not in dataframe.columns
    assert "slow_hla_sma" not in dataframe.columns
    assert "fast_hla_sma" not in dataframe.columns
    assert "high_low_avg" not in dataframe.columns
