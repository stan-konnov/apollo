import pandas as pd
import pytest

from apollo.calculations.conners_vix_expansion_contraction import (
    EngulfingVIXPatternCalculator,
)

UPSIDE_EXPANSION: float = 1.0
DOWNSIDE_CONTRACTION: float = -1.0
NO_SIGNIFICANT_MOVEMENT: float = 0.0


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__calculate_vix_expansion_contraction__for_correct_columns(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_vix_expansion_contraction method for correct columns.

    Resulting dataframe must have "cvec" column.
    Resulting dataframe must drop "vix_prev_open" and "vix_prev_close" columns.
    """

    cvec_calculator = EngulfingVIXPatternCalculator(
        dataframe=enhanced_dataframe,
        window_size=window_size,
    )

    cvec_calculator.calculate_vix_expansion_contraction()

    assert "cvec" in enhanced_dataframe.columns
    assert "vix_prev_open" not in enhanced_dataframe.columns
    assert "vix_prev_close" not in enhanced_dataframe.columns


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__calculate_vix_expansion_contraction__for_correct_rolling_window(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_vix_expansion_contraction method for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip WINDOW_SIZE - 1 rows for "cvec" column
    Since Contraction Expansion calculation must have at least N rows to be calculated.
    """

    cvec_calculator = EngulfingVIXPatternCalculator(
        dataframe=enhanced_dataframe,
        window_size=window_size,
    )

    cvec_calculator.calculate_vix_expansion_contraction()

    assert enhanced_dataframe["cvec"].isna().sum() == window_size - 1


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__calculate_vix_expansion_contraction__for_correct_cvec_calculation(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_vix_expansion_contraction method for correct Expansion Contraction.

    Resulting "cvec" column must have correct values for each row.
    """

    control_dataframe = enhanced_dataframe.copy()

    control_dataframe["vix_prev_open"] = control_dataframe["vix open"].shift(1)
    control_dataframe["vix_prev_close"] = control_dataframe["vix close"].shift(1)

    control_dataframe["cvec"] = (
        control_dataframe["adj close"]
        .rolling(
            window_size,
        )
        .apply(
            mimic_calc_cvec,
            args=(control_dataframe,),
        )
    )

    cvec_calculator = EngulfingVIXPatternCalculator(
        dataframe=enhanced_dataframe,
        window_size=window_size,
    )

    cvec_calculator.calculate_vix_expansion_contraction()

    pd.testing.assert_series_equal(
        control_dataframe["cvec"],
        enhanced_dataframe["cvec"],
    )


def mimic_calc_cvec(series: pd.Series, dataframe: pd.DataFrame) -> float:
    """
    Mimicry of Expansion Contraction calculation for testing purposes.

    Please see EngulfingVIXPatternCalculator for detailed explanation.
    """

    rolling_df = dataframe.loc[series.index]

    curr_open = rolling_df["vix open"].iloc[-1]
    curr_close = rolling_df["vix close"].iloc[-1]

    prev_open = rolling_df["vix_prev_open"].iloc[-1]
    prev_close = rolling_df["vix_prev_close"].iloc[-1]

    if curr_open < prev_open and curr_close > prev_close and curr_close > curr_open:
        return UPSIDE_EXPANSION

    if curr_open > prev_open and curr_close < prev_close and curr_close < curr_open:
        return DOWNSIDE_CONTRACTION

    return NO_SIGNIFICANT_MOVEMENT
