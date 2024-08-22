import pandas as pd
import pytest

from apollo.calculations.conners_vix_expansion_contraction import (
    ConnersVixExpansionContractionCalculator,
)


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

    cvec_calculator = ConnersVixExpansionContractionCalculator(
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

    cvec_calculator = ConnersVixExpansionContractionCalculator(
        dataframe=enhanced_dataframe,
        window_size=window_size,
    )

    cvec_calculator.calculate_vix_expansion_contraction()

    assert enhanced_dataframe["cvec"].isna().sum() == window_size - 1
