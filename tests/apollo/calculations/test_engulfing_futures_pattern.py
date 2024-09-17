import pandas as pd
import pytest

from apollo.calculations.combinatory_futures_patterns import (
    CombinatoryFuturesPatternsCalculator,
)
from apollo.settings import MISSING_DATA_PLACEHOLDER

NO_PATTERN: float = 0.0
BULLISH_ENGULFING: float = 1.0
BEARISH_ENGULFING: float = -1.0


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__calculate_engulfing_futures_pattern__for_correct_columns(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_engulfing_futures_pattern method for correct columns.

    Resulting dataframe must have "spfep" column.
    Resulting dataframe must drop "spf_prev_open" and "spf_prev_close" columns.
    """

    cfp_calculator = CombinatoryFuturesPatternsCalculator(
        dataframe=enhanced_dataframe,
        window_size=window_size,
        doji_threshold=0.005,
    )
    cfp_calculator.calculate_combinatory_futures_patterns()

    assert "spfep" in enhanced_dataframe.columns
    assert "spf_prev_open" not in enhanced_dataframe.columns
    assert "spf_prev_close" not in enhanced_dataframe.columns


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__calculate_engulfing_futures_pattern__for_correct_spfep_calculation(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_engulfing_futures_pattern method for correct Engulfing Pattern.

    Resulting "spfep" column must have correct values for each row.
    """

    control_dataframe = enhanced_dataframe.copy()

    control_dataframe["spfep"] = NO_PATTERN

    control_dataframe["spf_prev_open"] = 0.0
    control_dataframe["spf_prev_close"] = 0.0

    control_dataframe.loc[
        control_dataframe["spf open"] != MISSING_DATA_PLACEHOLDER,
        "spf_prev_open",
    ] = control_dataframe["spf open"].shift(1)

    control_dataframe.loc[
        control_dataframe["spf close"] != MISSING_DATA_PLACEHOLDER,
        "spf_prev_close",
    ] = control_dataframe["spf close"].shift(1)

    control_dataframe.loc[
        (
            (control_dataframe["spf open"] < control_dataframe["spf_prev_open"])
            & (control_dataframe["spf close"] > control_dataframe["spf_prev_close"])
            & (control_dataframe["spf close"] > control_dataframe["spf open"])
        ),
        "spfep",
    ] = BULLISH_ENGULFING

    control_dataframe.loc[
        (
            (control_dataframe["spf open"] > control_dataframe["spf_prev_open"])
            & (control_dataframe["spf close"] < control_dataframe["spf_prev_close"])
            & (control_dataframe["spf close"] < control_dataframe["spf open"])
        ),
        "spfep",
    ] = BEARISH_ENGULFING

    control_dataframe.drop(
        columns=["spf_prev_open", "spf_prev_close"],
        inplace=True,
    )

    cfp_calculator = CombinatoryFuturesPatternsCalculator(
        dataframe=enhanced_dataframe,
        window_size=window_size,
        doji_threshold=0.005,
    )
    cfp_calculator.calculate_combinatory_futures_patterns()

    pd.testing.assert_series_equal(
        control_dataframe["spfep"],
        enhanced_dataframe["spfep"],
    )


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__calculate_engulfing_futures_pattern__for_correct_missing_data_calculation(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_engulfing_futures_pattern method for missing data calculation.

    Resulting "spfep" column must have NO_PATTERN for rows with missing data.
    Resulting "spfep" column must have correct values for rows with valid data.
    """

    enhanced_dataframe.reset_index(inplace=True)

    # Mimic missing data for "spf open" and "spf close" columns
    enhanced_dataframe.loc[0:5, "spf open"] = MISSING_DATA_PLACEHOLDER
    enhanced_dataframe.loc[0:5, "spf close"] = MISSING_DATA_PLACEHOLDER

    control_dataframe = enhanced_dataframe.copy()

    control_dataframe["spfep"] = NO_PATTERN

    control_dataframe["spf_prev_open"] = 0.0
    control_dataframe["spf_prev_close"] = 0.0

    control_dataframe.loc[
        control_dataframe["spf open"] != MISSING_DATA_PLACEHOLDER,
        "spf_prev_open",
    ] = control_dataframe["spf open"].shift(1)

    control_dataframe.loc[
        control_dataframe["spf close"] != MISSING_DATA_PLACEHOLDER,
        "spf_prev_close",
    ] = control_dataframe["spf close"].shift(1)

    control_dataframe.loc[
        (
            (control_dataframe["spf open"] < control_dataframe["spf_prev_open"])
            & (control_dataframe["spf close"] > control_dataframe["spf_prev_close"])
            & (control_dataframe["spf close"] > control_dataframe["spf open"])
        ),
        "spfep",
    ] = BULLISH_ENGULFING

    control_dataframe.loc[
        (
            (control_dataframe["spf open"] > control_dataframe["spf_prev_open"])
            & (control_dataframe["spf close"] < control_dataframe["spf_prev_close"])
            & (control_dataframe["spf close"] < control_dataframe["spf open"])
        ),
        "spfep",
    ] = BEARISH_ENGULFING

    control_dataframe.drop(
        columns=["spf_prev_open", "spf_prev_close"],
        inplace=True,
    )

    cfp_calculator = CombinatoryFuturesPatternsCalculator(
        dataframe=enhanced_dataframe,
        window_size=window_size,
        doji_threshold=0.005,
    )
    cfp_calculator.calculate_combinatory_futures_patterns()

    assert all(enhanced_dataframe["spfep"].iloc[0:5] == NO_PATTERN)

    assert (
        control_dataframe["spfep"]
        .iloc[0:5]
        .equals(enhanced_dataframe["spfep"].iloc[0:5])
    )

    assert (
        control_dataframe["spfep"].iloc[6:].equals(enhanced_dataframe["spfep"].iloc[6:])
    )
