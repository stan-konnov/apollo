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
