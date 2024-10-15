import numpy as np
import pandas as pd
import pytest

from apollo.calculations.elliot_waves import ElliotWavesCalculator
from tests.utils.precalculate_shared_values import precalculate_shared_values

GOLDEN_RATIO: float = 1.618

NO_VALUE: float = 0.0

UP_TREND: float = 1.0
DOWN_TREND: float = -1.0

UPWARD_WAVE: float = 1.0
DOWNWARD_WAVE: float = -1.0

FAST_OSCILLATOR_PERIOD: int = 5
SLOW_OSCILLATOR_PERIOD: int = 10


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


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_elliot_waves__for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_elliot_waves method for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip WINDOW_SIZE - 1 rows for "ew" column
    Since Elliot Waves calculation must have at least N rows to be calculated.
    """

    dataframe = precalculate_shared_values(dataframe)

    ew_calculator = ElliotWavesCalculator(
        dataframe=dataframe,
        window_size=window_size,
        fast_oscillator_period=FAST_OSCILLATOR_PERIOD,
        slow_oscillator_period=SLOW_OSCILLATOR_PERIOD,
    )
    ew_calculator.calculate_elliot_waves()

    assert dataframe["ew"].isna().sum() == window_size - 1


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_elliot_waves__for_correct_elliot_waves_calculation(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_elliot_waves method for correct Elliot Waves calculation.

    Resulting "ew" column must have correct values for each row.
    """

    dataframe = precalculate_shared_values(dataframe)

    elliot_waves = np.full((1, window_size - 1), np.nan).flatten().tolist()
    elliot_waves_trend = np.full((1, window_size - 1), np.nan).flatten().tolist()

    control_dataframe = dataframe.copy()
    control_dataframe.reset_index(inplace=True)

    control_dataframe["high_low_avg"] = (
        control_dataframe["adj high"] + control_dataframe["adj low"]
    ) / 2

    control_dataframe["fast_hla_sma"] = (
        control_dataframe["high_low_avg"]
        .rolling(
            window=FAST_OSCILLATOR_PERIOD,
            min_periods=FAST_OSCILLATOR_PERIOD,
        )
        .mean()
    )

    control_dataframe["slow_hla_sma"] = (
        control_dataframe["high_low_avg"]
        .rolling(
            window=SLOW_OSCILLATOR_PERIOD,
            min_periods=SLOW_OSCILLATOR_PERIOD,
        )
        .mean()
    )

    control_dataframe["ewo"] = (
        control_dataframe["fast_hla_sma"] - control_dataframe["slow_hla_sma"]
    )

    control_dataframe["ewo_sma"] = (
        control_dataframe["ewo"]
        .rolling(
            window=window_size,
            min_periods=window_size,
        )
        .mean()
    )

    control_dataframe["adj close"].rolling(window_size).apply(
        mimic_calc_elliot_waves,
        args=(
            control_dataframe,
            elliot_waves,
            elliot_waves_trend,
        ),
    )

    control_dataframe["ew"] = elliot_waves
    control_dataframe.set_index("date", inplace=True)

    ew_calculator = ElliotWavesCalculator(
        dataframe=dataframe,
        window_size=window_size,
        fast_oscillator_period=FAST_OSCILLATOR_PERIOD,
        slow_oscillator_period=SLOW_OSCILLATOR_PERIOD,
    )
    ew_calculator.calculate_elliot_waves()

    pd.testing.assert_series_equal(dataframe["ew"], control_dataframe["ew"])


def mimic_calc_elliot_waves(
    series: pd.Series,
    dataframe: pd.DataFrame,
    elliot_waves: list[float],
    elliot_waves_trend: list[float],
) -> float:
    """
    Mimicry of Elliot Waves calculation for testing purposes.

    Please see ElliotWavesCalculator for
    detailed explanation of Elliot Waves calculation.
    """

    rolling_df = dataframe.loc[series.index]

    curr_wave = None
    curr_trend = None

    ewo_h = rolling_df["ewo"].max()
    ewo_l = rolling_df["ewo"].min()

    curr_ewo = rolling_df.iloc[-1]["ewo"]
    curr_ewo_sma = rolling_df.iloc[-1]["ewo_sma"]

    prev_trend = elliot_waves_trend[rolling_df.index[-2]]
    no_prev_trend = prev_trend == NO_VALUE or np.isnan(prev_trend)

    if no_prev_trend and curr_ewo == ewo_h:
        curr_trend = UP_TREND

    if (
        curr_ewo < curr_ewo_sma
        and prev_trend == DOWN_TREND
        and curr_ewo > GOLDEN_RATIO * ewo_l
    ):
        curr_trend = UP_TREND

    if no_prev_trend and curr_ewo == ewo_l:
        curr_trend = DOWN_TREND

    if (
        curr_ewo > curr_ewo_sma
        and prev_trend == UP_TREND
        and curr_ewo < GOLDEN_RATIO * ewo_h
    ):
        curr_trend = DOWN_TREND

    if curr_trend == UP_TREND and curr_ewo == ewo_h:
        curr_wave = UPWARD_WAVE

    if curr_trend == UP_TREND and curr_ewo == ewo_l:
        curr_wave = DOWNWARD_WAVE

    if curr_trend == DOWN_TREND and curr_ewo == ewo_l:
        curr_wave = UPWARD_WAVE

    if curr_trend == DOWN_TREND and curr_ewo == ewo_h:
        curr_wave = DOWNWARD_WAVE

    elliot_waves.append(curr_wave or NO_VALUE)
    elliot_waves_trend.append(curr_trend or NO_VALUE)

    return 0.0
