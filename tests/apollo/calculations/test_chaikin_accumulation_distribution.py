import pandas as pd
import pytest

from apollo.calculations.chaikin_accumulation_distribution import (
    ChaikinAccumulationDistributionCalculator,
)


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_chaikin_accumulation_distribution_line__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_chaikin_accumulation_distribution_line method for correct columns.

    Resulting dataframe must have columns "adl" and "prev_adl".
    """

    cad_calculator = ChaikinAccumulationDistributionCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    cad_calculator.calculate_chaikin_accumulation_distribution_line()

    assert "adl" in cad_calculator.dataframe.columns
    assert "prev_adl" in cad_calculator.dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_chaikin_accumulation_distribution_line__for_correct_rolling_window(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_chaikin_accumulation_distribution_line for correct rolling window.

    Where N = WINDOW_SIZE.

    Resulting dataframe must skip WINDOW_SIZE - 1 rows for adl column
    Since Chaikin Accumulation Distribution must have at least N rows to be calculated.

    Resulting dataframe must skip WINDOW_SIZE rows for prev_adl column
    Since previous AD line skips N + 1 rows due to shifting original AD line.
    """

    cad_calculator = ChaikinAccumulationDistributionCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )
    cad_calculator.calculate_chaikin_accumulation_distribution_line()

    assert dataframe["adl"].isna().sum() == window_size - 1
    assert dataframe["prev_adl"].isna().sum() == window_size
