from contextvars import ContextVar

import numpy as np
import pandas as pd
import pytest

from apollo.calculations.swing_events import SwingEventsCalculator

UP_SWING = 1.0
DOWN_SWING = -1.0
SWING_FILTER = 0.03
IN_DOWNSWING: ContextVar[bool] = ContextVar("IN_DOWNSWING", default=True)


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_swing_events__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_swing_events method for correct columns.

    Resulting dataframe must have "se" column.
    """

    sm_calculator = SwingEventsCalculator(
        dataframe=dataframe,
        window_size=window_size,
        swing_filter=SWING_FILTER,
    )

    sm_calculator.calculate_swing_events()

    assert "se" in dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_swing_events__for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_swing_events method for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip WINDOW_SIZE - 1 rows for SM column
    Since SM calculation must have at least N rows to be calculated.
    """

    sm_calculator = SwingEventsCalculator(
        dataframe=dataframe,
        window_size=window_size,
        swing_filter=SWING_FILTER,
    )

    sm_calculator.calculate_swing_events()

    assert dataframe["se"].isna().sum() == window_size - 1


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_swing_events__for_correct_atr_calculation(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_swing_events method for correct swings calculation.

    Resulting SM column must have correct values for each row.
    """

    control_dataframe = dataframe.copy()

    swing_l = control_dataframe.iloc[window_size - 2]["low"]
    swing_h = control_dataframe.iloc[window_size - 2]["high"]

    swing_events = np.full((1, window_size - 1), np.nan).flatten().tolist()

    control_dataframe["adj close"].rolling(window_size).apply(
        mimic_calc_se,
        args=(
            control_dataframe,
            swing_l,
            swing_h,
            swing_events,
        ),
    )

    control_dataframe["se"] = swing_events

    sm_calculator = SwingEventsCalculator(
        dataframe=dataframe,
        window_size=window_size,
        swing_filter=SWING_FILTER,
    )

    sm_calculator.calculate_swing_events()

    pd.testing.assert_series_equal(dataframe["se"], control_dataframe["se"])


def mimic_calc_se(
    series: pd.Series,
    dataframe: pd.DataFrame,
    swing_l: float,
    swing_h: float,
    swing_events: list[float],
) -> float:
    """
    Mimicry of swing events calculation for testing purposes.

    Please see SwingEventsCalculator for
    detailed explanation of swing events calculation.
    """

    rolling_df = dataframe.loc[series.index]

    current_low = rolling_df.iloc[-1]["low"]

    current_high = rolling_df.iloc[-1]["high"]

    current_swing_filter = rolling_df.iloc[-1]["adj close"] * SWING_FILTER

    if IN_DOWNSWING.get():

        if current_low < swing_l:

            swing_l = current_low

        if current_high - swing_l > current_swing_filter:

            IN_DOWNSWING.set(False)  # noqa: FBT003

            swing_l = current_low

            swing_h = current_high

            swing_events.append(UP_SWING)

            return 0.0

        swing_events.append(0.0)

        return 0.0

    if current_high > swing_h:

        swing_h = current_high

    if swing_h - current_low > current_swing_filter:

        IN_DOWNSWING.set(True)  # noqa: FBT003

        swing_events.append(DOWN_SWING)

        return 0.0

    swing_events.append(0.0)

    return 0.0
