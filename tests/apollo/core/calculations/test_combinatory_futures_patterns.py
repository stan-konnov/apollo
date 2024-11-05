import pandas as pd
import pytest

from apollo.core.calculations.combinatory_futures_patterns import (
    CombinatoryFuturesPatternsCalculator,
)
from apollo.settings import MISSING_DATA_PLACEHOLDER

NO_PATTERN: float = 0.0
BULLISH_PATTERN: float = 1.0
BEARISH_PATTERN: float = -1.0
DOJI_THRESHOLD: float = 0.005


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__calculate_combinatory_futures_patterns__for_correct_columns(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_combinatory_futures_patterns method for correct columns.

    Resulting dataframe must have following columns:
    "spf_ep", "spf_ep_tm1", "spf_tp", "spf_sp", "spf_sp_tm1".

    Resulting dataframe must drop following columns:
    "spf_open_tm1", "spf_close_tm1", "spf_open_tm2", "spf_close_tm2".
    """

    cfp_calculator = CombinatoryFuturesPatternsCalculator(
        dataframe=enhanced_dataframe,
        window_size=window_size,
        doji_threshold=DOJI_THRESHOLD,
    )
    cfp_calculator.calculate_combinatory_futures_patterns()

    assert "spf_ep" in enhanced_dataframe.columns
    assert "spf_ep_tm1" in enhanced_dataframe.columns

    assert "spf_tp" in enhanced_dataframe.columns

    assert "spf_sp" in enhanced_dataframe.columns
    assert "spf_sp_tm1" in enhanced_dataframe.columns

    assert "spf_open_tm1" not in enhanced_dataframe.columns
    assert "spf_open_tm2" not in enhanced_dataframe.columns
    assert "spf_close_tm1" not in enhanced_dataframe.columns
    assert "spf_close_tm2" not in enhanced_dataframe.columns


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__calculate_combinatory_futures_patterns__for_correct_patterns_calculation(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_combinatory_futures_patterns method for correct patterns calculation.

    Following columns must have correct values for each row:
    "spf_ep", "spf_ep_tm1", "spf_tp", "spf_sp", "spf_sp_tm1".
    """

    control_dataframe = enhanced_dataframe.copy()

    control_dataframe["spf_ep"] = NO_PATTERN
    control_dataframe["spf_sp"] = NO_PATTERN
    control_dataframe["spf_tp"] = NO_PATTERN

    control_dataframe["spf_open_tm1"] = 0.0
    control_dataframe["spf_open_tm2"] = 0.0

    control_dataframe["spf_close_tm1"] = 0.0
    control_dataframe["spf_close_tm2"] = 0.0

    control_dataframe.loc[
        control_dataframe["spf open"] != MISSING_DATA_PLACEHOLDER,
        "spf_open_tm1",
    ] = control_dataframe["spf open"].shift(1)

    control_dataframe.loc[
        control_dataframe["spf open"] != MISSING_DATA_PLACEHOLDER,
        "spf_open_tm2",
    ] = control_dataframe["spf open"].shift(2)

    control_dataframe.loc[
        control_dataframe["spf close"] != MISSING_DATA_PLACEHOLDER,
        "spf_close_tm1",
    ] = control_dataframe["spf close"].shift(1)

    control_dataframe.loc[
        control_dataframe["spf close"] != MISSING_DATA_PLACEHOLDER,
        "spf_close_tm2",
    ] = control_dataframe["spf close"].shift(2)

    open_on_close_midpoint_tm2 = (
        control_dataframe["spf_open_tm2"] + control_dataframe["spf_close_tm2"]
    ) / 2

    bullish_engulfing = (
        (control_dataframe["spf open"] < control_dataframe["spf_open_tm1"])
        & (control_dataframe["spf close"] > control_dataframe["spf_close_tm1"])
        & (control_dataframe["spf close"] > control_dataframe["spf open"])
    )

    bearish_engulfing = (
        (control_dataframe["spf open"] > control_dataframe["spf_open_tm1"])
        & (control_dataframe["spf close"] < control_dataframe["spf_close_tm1"])
        & (control_dataframe["spf close"] < control_dataframe["spf open"])
    )

    bullish_morning_star = (
        (control_dataframe["spf_close_tm2"] < control_dataframe["spf_open_tm2"])
        & (
            abs(control_dataframe["spf_close_tm1"] - control_dataframe["spf_open_tm1"])
            / control_dataframe["spf_open_tm1"]
            < DOJI_THRESHOLD
        )
        & (control_dataframe["spf close"] > control_dataframe["spf open"])
        & (control_dataframe["spf close"] > open_on_close_midpoint_tm2)
    )

    bearish_evening_star = (
        (control_dataframe["spf_close_tm2"] > control_dataframe["spf_open_tm2"])
        & (
            abs(control_dataframe["spf_close_tm1"] - control_dataframe["spf_open_tm1"])
            / control_dataframe["spf_open_tm1"]
            < DOJI_THRESHOLD
        )
        & (control_dataframe["spf close"] < control_dataframe["spf open"])
        & (control_dataframe["spf close"] < open_on_close_midpoint_tm2)
    )

    three_white_soldiers = (
        (control_dataframe["spf close"] > control_dataframe["spf open"])
        & (control_dataframe["spf_close_tm1"] > control_dataframe["spf_open_tm1"])
        & (control_dataframe["spf_close_tm2"] > control_dataframe["spf_open_tm2"])
        & (control_dataframe["spf close"] > control_dataframe["spf_close_tm1"])
        & (control_dataframe["spf_close_tm1"] > control_dataframe["spf_close_tm2"])
        & (control_dataframe["spf open"] <= control_dataframe["spf_close_tm1"])
        & (control_dataframe["spf_open_tm1"] <= control_dataframe["spf_close_tm2"])
    )

    three_black_soldiers = (
        (control_dataframe["spf close"] < control_dataframe["spf open"])
        & (control_dataframe["spf_close_tm1"] < control_dataframe["spf_open_tm1"])
        & (control_dataframe["spf_close_tm2"] < control_dataframe["spf_open_tm2"])
        & (control_dataframe["spf close"] < control_dataframe["spf_close_tm1"])
        & (control_dataframe["spf_close_tm1"] < control_dataframe["spf_close_tm2"])
        & (control_dataframe["spf open"] >= control_dataframe["spf_close_tm1"])
        & (control_dataframe["spf_open_tm1"] >= control_dataframe["spf_close_tm2"])
    )

    control_dataframe.loc[bullish_engulfing, "spf_ep"] = BULLISH_PATTERN
    control_dataframe.loc[bearish_engulfing, "spf_ep"] = BEARISH_PATTERN

    control_dataframe.loc[bullish_morning_star, "spf_sp"] = BULLISH_PATTERN
    control_dataframe.loc[bearish_evening_star, "spf_sp"] = BEARISH_PATTERN

    control_dataframe.loc[three_white_soldiers, "spf_tp"] = BULLISH_PATTERN
    control_dataframe.loc[three_black_soldiers, "spf_tp"] = BEARISH_PATTERN

    control_dataframe["spf_ep_tm1"] = control_dataframe["spf_ep"].shift(1)
    control_dataframe["spf_sp_tm1"] = control_dataframe["spf_sp"].shift(1)

    control_dataframe.drop(
        columns=["spf_open_tm1", "spf_open_tm2", "spf_close_tm1", "spf_close_tm2"],
        inplace=True,
    )

    cfp_calculator = CombinatoryFuturesPatternsCalculator(
        dataframe=enhanced_dataframe,
        window_size=window_size,
        doji_threshold=DOJI_THRESHOLD,
    )
    cfp_calculator.calculate_combinatory_futures_patterns()

    pd.testing.assert_series_equal(
        control_dataframe["spf_ep"],
        enhanced_dataframe["spf_ep"],
    )
    pd.testing.assert_series_equal(
        control_dataframe["spf_ep_tm1"],
        enhanced_dataframe["spf_ep_tm1"],
    )

    pd.testing.assert_series_equal(
        control_dataframe["spf_sp"],
        enhanced_dataframe["spf_sp"],
    )
    pd.testing.assert_series_equal(
        control_dataframe["spf_sp_tm1"],
        enhanced_dataframe["spf_sp_tm1"],
    )

    pd.testing.assert_series_equal(
        control_dataframe["spf_tp"],
        enhanced_dataframe["spf_tp"],
    )


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__calculate_combinatory_futures_patterns__for_correct_missing_data_calculation(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_combinatory_futures_patterns method for missing data calculation.

    Following columns must have NO_PATTERN for rows with missing data:
    "spf_ep", "spf_ep_tm1", "spf_tp", "spf_sp", "spf_sp_tm1".

    Following columns must have correct values for rows with valid data:
    "spf_ep", "spf_ep_tm1", "spf_tp", "spf_sp", "spf_sp_tm1".
    """

    enhanced_dataframe.reset_index(inplace=True)

    # Mimic missing data for "spf open" and "spf close" columns
    enhanced_dataframe.loc[0:5, "spf open"] = MISSING_DATA_PLACEHOLDER
    enhanced_dataframe.loc[0:5, "spf close"] = MISSING_DATA_PLACEHOLDER

    control_dataframe = enhanced_dataframe.copy()

    control_dataframe["spf_ep"] = NO_PATTERN
    control_dataframe["spf_sp"] = NO_PATTERN
    control_dataframe["spf_tp"] = NO_PATTERN

    control_dataframe["spf_open_tm1"] = 0.0
    control_dataframe["spf_open_tm2"] = 0.0

    control_dataframe["spf_close_tm1"] = 0.0
    control_dataframe["spf_close_tm2"] = 0.0

    control_dataframe.loc[
        control_dataframe["spf open"] != MISSING_DATA_PLACEHOLDER,
        "spf_open_tm1",
    ] = control_dataframe["spf open"].shift(1)

    control_dataframe.loc[
        control_dataframe["spf open"] != MISSING_DATA_PLACEHOLDER,
        "spf_open_tm2",
    ] = control_dataframe["spf open"].shift(2)

    control_dataframe.loc[
        control_dataframe["spf close"] != MISSING_DATA_PLACEHOLDER,
        "spf_close_tm1",
    ] = control_dataframe["spf close"].shift(1)

    control_dataframe.loc[
        control_dataframe["spf close"] != MISSING_DATA_PLACEHOLDER,
        "spf_close_tm2",
    ] = control_dataframe["spf close"].shift(2)

    open_on_close_midpoint_tm2 = (
        control_dataframe["spf_open_tm2"] + control_dataframe["spf_close_tm2"]
    ) / 2

    bullish_engulfing = (
        (control_dataframe["spf open"] < control_dataframe["spf_open_tm1"])
        & (control_dataframe["spf close"] > control_dataframe["spf_close_tm1"])
        & (control_dataframe["spf close"] > control_dataframe["spf open"])
    )

    bearish_engulfing = (
        (control_dataframe["spf open"] > control_dataframe["spf_open_tm1"])
        & (control_dataframe["spf close"] < control_dataframe["spf_close_tm1"])
        & (control_dataframe["spf close"] < control_dataframe["spf open"])
    )

    bullish_morning_star = (
        (control_dataframe["spf_close_tm2"] < control_dataframe["spf_open_tm2"])
        & (
            abs(control_dataframe["spf_close_tm1"] - control_dataframe["spf_open_tm1"])
            / control_dataframe["spf_open_tm1"]
            < DOJI_THRESHOLD
        )
        & (control_dataframe["spf close"] > control_dataframe["spf open"])
        & (control_dataframe["spf close"] > open_on_close_midpoint_tm2)
    )

    bearish_evening_star = (
        (control_dataframe["spf_close_tm2"] > control_dataframe["spf_open_tm2"])
        & (
            abs(control_dataframe["spf_close_tm1"] - control_dataframe["spf_open_tm1"])
            / control_dataframe["spf_open_tm1"]
            < DOJI_THRESHOLD
        )
        & (control_dataframe["spf close"] < control_dataframe["spf open"])
        & (control_dataframe["spf close"] < open_on_close_midpoint_tm2)
    )

    three_white_soldiers = (
        (control_dataframe["spf close"] > control_dataframe["spf open"])
        & (control_dataframe["spf_close_tm1"] > control_dataframe["spf_open_tm1"])
        & (control_dataframe["spf_close_tm2"] > control_dataframe["spf_open_tm2"])
        & (control_dataframe["spf close"] > control_dataframe["spf_close_tm1"])
        & (control_dataframe["spf_close_tm1"] > control_dataframe["spf_close_tm2"])
        & (control_dataframe["spf open"] <= control_dataframe["spf_close_tm1"])
        & (control_dataframe["spf_open_tm1"] <= control_dataframe["spf_close_tm2"])
    )

    three_black_soldiers = (
        (control_dataframe["spf close"] < control_dataframe["spf open"])
        & (control_dataframe["spf_close_tm1"] < control_dataframe["spf_open_tm1"])
        & (control_dataframe["spf_close_tm2"] < control_dataframe["spf_open_tm2"])
        & (control_dataframe["spf close"] < control_dataframe["spf_close_tm1"])
        & (control_dataframe["spf_close_tm1"] < control_dataframe["spf_close_tm2"])
        & (control_dataframe["spf open"] >= control_dataframe["spf_close_tm1"])
        & (control_dataframe["spf_open_tm1"] >= control_dataframe["spf_close_tm2"])
    )

    control_dataframe.loc[bullish_engulfing, "spf_ep"] = BULLISH_PATTERN
    control_dataframe.loc[bearish_engulfing, "spf_ep"] = BEARISH_PATTERN

    control_dataframe.loc[bullish_morning_star, "spf_sp"] = BULLISH_PATTERN
    control_dataframe.loc[bearish_evening_star, "spf_sp"] = BEARISH_PATTERN

    control_dataframe.loc[three_white_soldiers, "spf_tp"] = BULLISH_PATTERN
    control_dataframe.loc[three_black_soldiers, "spf_tp"] = BEARISH_PATTERN

    control_dataframe["spf_ep_tm1"] = control_dataframe["spf_ep"].shift(1)
    control_dataframe["spf_sp_tm1"] = control_dataframe["spf_sp"].shift(1)

    control_dataframe.drop(
        columns=["spf_open_tm1", "spf_open_tm2", "spf_close_tm1", "spf_close_tm2"],
        inplace=True,
    )

    cfp_calculator = CombinatoryFuturesPatternsCalculator(
        dataframe=enhanced_dataframe,
        window_size=window_size,
        doji_threshold=DOJI_THRESHOLD,
    )
    cfp_calculator.calculate_combinatory_futures_patterns()

    assert all(enhanced_dataframe["spf_ep"].iloc[0:5] == NO_PATTERN)
    assert all(enhanced_dataframe["spf_sp"].iloc[0:5] == NO_PATTERN)
    assert all(enhanced_dataframe["spf_tp"].iloc[0:5] == NO_PATTERN)

    assert (
        control_dataframe["spf_ep"]
        .iloc[0:5]
        .equals(enhanced_dataframe["spf_ep"].iloc[0:5])
    )
    assert (
        control_dataframe["spf_sp"]
        .iloc[0:5]
        .equals(enhanced_dataframe["spf_sp"].iloc[0:5])
    )
    assert (
        control_dataframe["spf_tp"]
        .iloc[0:5]
        .equals(enhanced_dataframe["spf_tp"].iloc[0:5])
    )
    assert (
        control_dataframe["spf_ep_tm1"]
        .iloc[0:5]
        .equals(enhanced_dataframe["spf_ep_tm1"].iloc[0:5])
    )
    assert (
        control_dataframe["spf_sp_tm1"]
        .iloc[0:5]
        .equals(enhanced_dataframe["spf_sp_tm1"].iloc[0:5])
    )

    assert (
        control_dataframe["spf_ep"]
        .iloc[6:]
        .equals(enhanced_dataframe["spf_ep"].iloc[6:])
    )
    assert (
        control_dataframe["spf_sp"]
        .iloc[6:]
        .equals(enhanced_dataframe["spf_sp"].iloc[6:])
    )
    assert (
        control_dataframe["spf_tp"]
        .iloc[6:]
        .equals(enhanced_dataframe["spf_tp"].iloc[6:])
    )
    assert (
        control_dataframe["spf_ep_tm1"]
        .iloc[6:]
        .equals(enhanced_dataframe["spf_ep_tm1"].iloc[6:])
    )
    assert (
        control_dataframe["spf_sp_tm1"]
        .iloc[6:]
        .equals(enhanced_dataframe["spf_sp_tm1"].iloc[6:])
    )
