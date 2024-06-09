import numpy as np
import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.hull_moving_average import (
    HullMovingAverageCalculator,
)
from apollo.calculations.keltner_channel import KeltnerChannelCalculator

VOLATILITY_MULTIPLIER = 0.5


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_keltner_channel__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_keltner_channel method for correct columns.

    Resulting dataframe must have columns "lkc_bound" and "ukc_bound".
    """

    hma_calculator = HullMovingAverageCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    hma_calculator.calculate_hull_moving_average()

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    atr_calculator.calculate_average_true_range()

    kc_calculator = KeltnerChannelCalculator(
        dataframe=dataframe,
        window_size=window_size,
        volatility_multiplier=VOLATILITY_MULTIPLIER,
    )
    kc_calculator.calculate_keltner_channel()

    assert "lkc_bound" in kc_calculator.dataframe.columns
    assert "ukc_bound" in kc_calculator.dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_keltner_channel__for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_keltner_channel method for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip (WINDOW_SIZE - 1) * 2 rows for lkc_bound ukc_bound
    Since Keltner Channel calculation must have at least N rows of valid
    ATR calculation that is based on TR calculation.
    """

    hma_calculator = HullMovingAverageCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    hma_calculator.calculate_hull_moving_average()

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    atr_calculator.calculate_average_true_range()

    kc_calculator = KeltnerChannelCalculator(
        dataframe=dataframe,
        window_size=window_size,
        volatility_multiplier=VOLATILITY_MULTIPLIER,
    )
    kc_calculator.calculate_keltner_channel()

    assert dataframe["lkc_bound"].isna().sum() == (window_size - 1) * 2
    assert dataframe["ukc_bound"].isna().sum() == (window_size - 1) * 2


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_keltner_channel__for_correct_kc_calculation(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_keltner_channel method for correct Keltner Channel calculation.

    Resulting "lkc_bound" and "ukc_bound" columns must have correct values for each row.
    """

    lkc_bound = np.full((1, window_size - 1), np.nan).flatten().tolist()
    ukc_bound = np.full((1, window_size - 1), np.nan).flatten().tolist()

    control_dataframe = dataframe.copy()

    hma_calculator = HullMovingAverageCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    hma_calculator.calculate_hull_moving_average()

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=control_dataframe,
        window_size=window_size,
    )
    atr_calculator.calculate_average_true_range()

    control_dataframe["adj close"].rolling(window_size).apply(
        mimic_calc_chan,
        args=(
            control_dataframe,
            lkc_bound,
            ukc_bound,
            VOLATILITY_MULTIPLIER,
        ),
    )

    control_dataframe["lkc_bound"] = lkc_bound
    control_dataframe["ukc_bound"] = ukc_bound

    hma_calculator = HullMovingAverageCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    hma_calculator.calculate_hull_moving_average()

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    atr_calculator.calculate_average_true_range()

    kc_calculator = KeltnerChannelCalculator(
        dataframe=dataframe,
        window_size=window_size,
        volatility_multiplier=VOLATILITY_MULTIPLIER,
    )
    kc_calculator.calculate_keltner_channel()

    pd.testing.assert_series_equal(
        dataframe["lkc_bound"],
        control_dataframe["lkc_bound"],
    )
    pd.testing.assert_series_equal(
        dataframe["ukc_bound"],
        control_dataframe["ukc_bound"],
    )


def mimic_calc_chan(
    series: pd.Series,
    dataframe: pd.DataFrame,
    lkc_bound: list[float],
    ukc_bound: list[float],
    volatility_multiplier: float,
) -> float:
    """
    Mimicry of Keltner Channel calculation for testing purposes.

    Please see KeltnerChannelCalculator for
    detailed explanation of Keltner Channel calculation.
    """

    rolling_df = dataframe.loc[series.index]

    l_band = rolling_df["hma"] - rolling_df["atr"] * volatility_multiplier
    u_band = rolling_df["hma"] + rolling_df["atr"] * volatility_multiplier

    lkc_bound.append(l_band[-1])
    ukc_bound.append(u_band[-1])

    return 0.0
