import pandas as pd
import pytest

from apollo.calculations.engulfing_vix_pattern import (
    EngulfingVIXPatternCalculator,
)
from apollo.settings import MISSING_DATA_PLACEHOLDER

NO_PATTERN: float = 0.0
BULLISH_ENGULFING: float = 1.0
BEARISH_ENGULFING: float = -1.0

"""
TODO: All new calculators should test for not calculating over missing data
"""


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__calculate_engulfing_vix_pattern__for_correct_columns(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_engulfing_vix_pattern method for correct columns.

    Resulting dataframe must have "vixep" column.
    Resulting dataframe must drop "vix_prev_open" and "vix_prev_close" columns.
    """

    evp_calculator = EngulfingVIXPatternCalculator(
        dataframe=enhanced_dataframe,
        window_size=window_size,
    )

    evp_calculator.calculate_engulfing_vix_pattern()

    assert "vixep" in enhanced_dataframe.columns
    assert "vix_prev_open" not in enhanced_dataframe.columns
    assert "vix_prev_close" not in enhanced_dataframe.columns


@pytest.mark.usefixtures("enhanced_dataframe", "window_size")
def test__calculate_engulfing_vix_pattern__for_correct_cvec_calculation(
    enhanced_dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_engulfing_vix_pattern method for correct Engulfing Pattern.

    Resulting "vixep" column must have correct values for each row.
    """

    control_dataframe = enhanced_dataframe.copy()

    control_dataframe["vixep"] = NO_PATTERN

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
        "vixep",
    ] = BULLISH_ENGULFING

    control_dataframe.loc[
        (
            (control_dataframe["vix open"] > control_dataframe["vix_prev_open"])
            & (control_dataframe["vix close"] < control_dataframe["vix_prev_close"])
            & (control_dataframe["vix close"] < control_dataframe["vix open"])
        ),
        "vixep",
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
        control_dataframe["vixep"],
        enhanced_dataframe["vixep"],
    )
