import numpy as np
import pandas as pd
import pytest

from apollo.calculations.wilders_swing_index import WildersSwingIndexCalculator

LOW_SWING_POINT: float = -1.0
HIGH_SWING_POINT: float = 1.0

WEIGHTED_TR_MULTIPLIER: float = 0.1
WEIGHTED_TR_MULTIPLIER_CURR: float = 1.0 - WEIGHTED_TR_MULTIPLIER
WEIGHTED_TR_MULTIPLIER_PREV: float = 0.0 + WEIGHTED_TR_MULTIPLIER


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_swing_index__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_swing_index method for correct columns.

    Resulting dataframe must have "sp" column.
    Resulting dataframe must not have "si", "asi", "prev_open", "prev_close" columns.
    """

    wsi_calculator = WildersSwingIndexCalculator(
        dataframe=dataframe,
        window_size=window_size,
        weighted_tr_multiplier=WEIGHTED_TR_MULTIPLIER,
    )

    wsi_calculator.calculate_swing_index()

    assert "sp" in dataframe.columns
    assert "si" not in dataframe.columns
    assert "asi" not in dataframe.columns
    assert "prev_open" not in dataframe.columns
    assert "prev_close" not in dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_swing_index__for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_swing_index method for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip WINDOW_SIZE rows for SP column
    Since SP calculation relies on 3 consecutive ASI values,
    and, in such, only available after first N rows.
    """

    wsi_calculator = WildersSwingIndexCalculator(
        dataframe=dataframe,
        window_size=window_size,
        weighted_tr_multiplier=WEIGHTED_TR_MULTIPLIER,
    )

    wsi_calculator.calculate_swing_index()

    assert dataframe["sp"].isna().sum() == window_size


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calc_wtr__with_invalid_base_calculation(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calc_wtr method with invalid base calculation.

    The provided value for calculation of Weighted True Range is invalid.

    WildersSwingIndexCalculator must raise ValueError if base calculation is invalid.
    """

    wsi_calculator = WildersSwingIndexCalculator(
        dataframe=dataframe,
        window_size=window_size,
        weighted_tr_multiplier=WEIGHTED_TR_MULTIPLIER,
    )

    exception_message = "Provided diff_index is invalid. Base calculation is faulty."

    with pytest.raises(
        ValueError,
        match=exception_message,
    ) as exception:
        wsi_calculator._calc_wtr(999, 1, 1, 1, 1)  # noqa: SLF001

    assert str(exception.value) == exception_message


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_swing_index__for_correct_sp_calculation(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_swing_index method for correct SP calculation.

    Resulting SP column must have correct values for each row.
    """

    control_dataframe = dataframe.copy()

    swing_points: list[float] = np.full((1, window_size - 1), np.nan).flatten().tolist()

    control_dataframe["prev_open"] = control_dataframe["adj open"].shift(1)
    control_dataframe["prev_close"] = control_dataframe["adj close"].shift(1)

    control_dataframe["si"] = (
        control_dataframe["adj close"]
        .rolling(window_size)
        .apply(
            mimic_calc_si,
            args=(control_dataframe,),
        )
    )

    control_dataframe["asi"] = (
        control_dataframe["adj close"]
        .rolling(window_size)
        .apply(
            mimic_calc_asi,
            args=(control_dataframe,),
        )
    )

    control_dataframe["adj close"].rolling(window_size).apply(
        mimic_calc_hlsp,
        args=(control_dataframe, window_size, swing_points),
    )

    control_dataframe["sp"] = swing_points
    control_dataframe["sp"] = control_dataframe["sp"].shift(1)

    control_dataframe.drop(
        columns=["si", "asi", "prev_open", "prev_close"],
        inplace=True,
    )

    wsi_calculator = WildersSwingIndexCalculator(
        dataframe=dataframe,
        window_size=window_size,
        weighted_tr_multiplier=WEIGHTED_TR_MULTIPLIER,
    )

    wsi_calculator.calculate_swing_index()

    pd.testing.assert_series_equal(dataframe["sp"], control_dataframe["sp"])


def mimic_calc_si(series: pd.Series, dataframe: pd.DataFrame) -> float:
    """
    Mimicry of SI calculation for testing purposes.

    Please see WildersSwingIndexCalculator for detailed explanation of TR calculation.
    """

    rolling_df = dataframe.loc[series.index]

    curr_open: float = rolling_df.iloc[-1]["adj open"]
    curr_high: float = rolling_df.iloc[-1]["adj high"]
    curr_low: float = rolling_df.iloc[-1]["adj low"]
    curr_close: float = rolling_df.iloc[-1]["adj close"]

    prev_open: float = rolling_df.iloc[-1]["prev_open"]
    prev_close: float = rolling_df.iloc[-1]["prev_close"]

    absolute_differences = [
        abs(difference)
        for difference in [
            curr_high - prev_close,
            curr_low - prev_close,
            curr_high - curr_low,
        ]
    ]

    highest_value = max(absolute_differences)

    highest_value_index = absolute_differences.index(highest_value)

    weighted_true_range = mimic_calc_wtr(
        highest_value_index,
        curr_high,
        curr_low,
        prev_close,
        prev_open,
    )

    return (
        (
            (curr_close - prev_close)
            + (WEIGHTED_TR_MULTIPLIER * (curr_close - curr_open))
            + (WEIGHTED_TR_MULTIPLIER * (prev_close - prev_open))
        )
        / weighted_true_range
    ) * highest_value


def mimic_calc_wtr(
    diff_index: int,
    curr_high: float,
    curr_low: float,
    prev_close: float,
    prev_open: float,
) -> float:
    """
    Mimicry of WTR calculation for testing purposes.

    Please see WildersSwingIndexCalculator for detailed explanation of WTR calculation.
    """

    match diff_index:
        case 0:
            return (
                abs(curr_high - prev_close)
                - WEIGHTED_TR_MULTIPLIER_CURR * abs(curr_low - prev_close)
                + WEIGHTED_TR_MULTIPLIER_PREV * abs(prev_close - prev_open)
            )
        case 1:
            return (
                abs(curr_low - prev_close)
                - WEIGHTED_TR_MULTIPLIER_CURR * abs(curr_high - prev_close)
                + WEIGHTED_TR_MULTIPLIER_PREV * abs(prev_close - prev_open)
            )
        case 2:
            return abs(
                curr_high - curr_low,
            ) + WEIGHTED_TR_MULTIPLIER_PREV * abs(prev_close - prev_open)
        case _:
            raise ValueError(
                "Provided diff_index is invalid. Base calculation is faulty.",
            )


def mimic_calc_asi(series: pd.Series, dataframe: pd.DataFrame) -> float:
    """
    Mimicry of ASI calculation for testing purposes.

    Please see WildersSwingIndexCalculator for detailed explanation of ASI calculation.
    """

    rolling_df = dataframe.loc[series.index]
    return rolling_df["si"].sum()


def mimic_calc_hlsp(
    series: pd.Series,
    dataframe: pd.DataFrame,
    window_size: int,
    swing_points: list[float],
) -> float:
    """
    Mimicry of HLSP calculation for testing purposes.

    Please see WildersSwingIndexCalculator for detailed explanation of HLSP calculation.
    """

    rolling_df = dataframe.loc[series.index]

    left, middle, right = list(
        rolling_df.iloc[window_size - 3 :]["asi"],
    )

    if middle > left and middle > right:
        swing_points.append(HIGH_SWING_POINT)

    elif middle < left and middle < right:
        swing_points.append(LOW_SWING_POINT)

    else:
        swing_points.append(0.0)

    return 0.0
