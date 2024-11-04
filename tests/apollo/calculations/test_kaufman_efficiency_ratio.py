import pandas as pd
import pytest

from apollo.calculations.kaufman_efficiency_ratio import (
    KaufmanEfficiencyRatioCalculator,
)


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_kaufman_efficiency_ratio__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_kaufman_efficiency_ratio method for correct columns.

    Resulting dataframe must have "ker" column.
    """
    ker_calculator = KaufmanEfficiencyRatioCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    ker_calculator.calculate_kaufman_efficiency_ratio()

    assert "ker" in dataframe.columns
