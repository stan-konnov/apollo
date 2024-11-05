import pandas as pd
import pytest

from apollo.core.calculators.engulfing_vix_pattern import (
    EngulfingVIXPatternCalculator,
)
from apollo.settings import MISSING_DATA_PLACEHOLDER

NO_PATTERN: float = 0.0
BULLISH_ENGULFING: float = 1.0
BEARISH_ENGULFING: float = -1.0


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__calculate_engulfing_vix_pattern__for_correct_columns(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_engulfing_vix_pattern method for correct columns.

    Resulting dataframe must have "vix_ep" column.
    Resulting dataframe must drop "vix_prev_open" and "vix_prev_close" columns.
    """

    evp_calculator = EngulfingVIXPatternCalculator(
        dataframe=enhanced_dataframe,
        window_size=window_size,
    )

    evp_calculator.calculate_engulfing_vix_pattern()

    assert "vix_ep" in enhanced_dataframe.columns
    assert "vix_prev_open" not in enhanced_dataframe.columns
    assert "vix_prev_close" not in enhanced_dataframe.columns


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__calculate_engulfing_vix_pattern__for_correct_vix_ep_calculation(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_engulfing_vix_pattern method for correct Engulfing Pattern.

    Resulting "vix_ep" column must have correct values for each row.
    """

    control_dataframe = enhanced_dataframe.copy()

    control_dataframe["vix_ep"] = NO_PATTERN

    control_dataframe["vix_prev_open"] = 0.0
    control_dataframe["vix_prev_close"] = 0.0

    control_dataframe.loc[
        control_dataframe["vix open"] != MISSING_DATA_PLACEHOLDER,
        "vix_prev_open",
    ] = control_dataframe["vix open"].shift(1)

    control_dataframe.loc[
        control_dataframe["vix close"] != MISSING_DATA_PLACEHOLDER,
        "vix_prev_close",
    ] = control_dataframe["vix close"].shift(1)

    control_dataframe.loc[
        (
            (control_dataframe["vix open"] < control_dataframe["vix_prev_open"])
            & (control_dataframe["vix close"] > control_dataframe["vix_prev_close"])
            & (control_dataframe["vix close"] > control_dataframe["vix open"])
        ),
        "vix_ep",
    ] = BULLISH_ENGULFING

    control_dataframe.loc[
        (
            (control_dataframe["vix open"] > control_dataframe["vix_prev_open"])
            & (control_dataframe["vix close"] < control_dataframe["vix_prev_close"])
            & (control_dataframe["vix close"] < control_dataframe["vix open"])
        ),
        "vix_ep",
    ] = BEARISH_ENGULFING

    control_dataframe.drop(
        columns=["vix_prev_open", "vix_prev_close"],
        inplace=True,
    )

    evp_calculator = EngulfingVIXPatternCalculator(
        dataframe=enhanced_dataframe,
        window_size=window_size,
    )

    evp_calculator.calculate_engulfing_vix_pattern()

    pd.testing.assert_series_equal(
        control_dataframe["vix_ep"],
        enhanced_dataframe["vix_ep"],
    )


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__calculate_engulfing_vix_pattern__for_correct_missing_data_calculation(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_engulfing_vix_pattern method for correct missing data calculation.

    Resulting "vix_ep" column must have NO_PATTERN for rows with missing data.
    Resulting "vix_ep" column must have correct values for rows with valid data.
    """

    enhanced_dataframe.reset_index(inplace=True)

    # Mimic missing data for "vix open" and "vix close" columns
    enhanced_dataframe.loc[0:5, "vix open"] = MISSING_DATA_PLACEHOLDER
    enhanced_dataframe.loc[0:5, "vix close"] = MISSING_DATA_PLACEHOLDER

    control_dataframe = enhanced_dataframe.copy()

    control_dataframe["vix_ep"] = NO_PATTERN

    control_dataframe["vix_prev_open"] = 0.0
    control_dataframe["vix_prev_close"] = 0.0

    control_dataframe.loc[
        control_dataframe["vix open"] != MISSING_DATA_PLACEHOLDER,
        "vix_prev_open",
    ] = control_dataframe["vix open"].shift(1)

    control_dataframe.loc[
        control_dataframe["vix close"] != MISSING_DATA_PLACEHOLDER,
        "vix_prev_close",
    ] = control_dataframe["vix close"].shift(1)

    control_dataframe.loc[
        (
            (control_dataframe["vix open"] < control_dataframe["vix_prev_open"])
            & (control_dataframe["vix close"] > control_dataframe["vix_prev_close"])
            & (control_dataframe["vix close"] > control_dataframe["vix open"])
        ),
        "vix_ep",
    ] = BULLISH_ENGULFING

    control_dataframe.loc[
        (
            (control_dataframe["vix open"] > control_dataframe["vix_prev_open"])
            & (control_dataframe["vix close"] < control_dataframe["vix_prev_close"])
            & (control_dataframe["vix close"] < control_dataframe["vix open"])
        ),
        "vix_ep",
    ] = BEARISH_ENGULFING

    control_dataframe.drop(
        columns=["vix_prev_open", "vix_prev_close"],
        inplace=True,
    )

    evp_calculator = EngulfingVIXPatternCalculator(
        dataframe=enhanced_dataframe,
        window_size=window_size,
    )

    evp_calculator.calculate_engulfing_vix_pattern()

    assert all(enhanced_dataframe["vix_ep"].iloc[0:5] == NO_PATTERN)

    assert (
        control_dataframe["vix_ep"]
        .iloc[0:5]
        .equals(enhanced_dataframe["vix_ep"].iloc[0:5])
    )

    assert (
        control_dataframe["vix_ep"]
        .iloc[6:]
        .equals(enhanced_dataframe["vix_ep"].iloc[6:])
    )
