import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator


@pytest.mark.usefixtures("dataframe", "window_size")
def test__calculate_average_true_range__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test calculate_average_true_range method for correct columns.

    Resulting dataframe must have columns "tr" and "atr".
    Resulting dataframe must drop "prev_close" column.
    """

    atr_calculator = AverageTrueRangeCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    atr_calculator.calculate_average_true_range()

    assert "tr" in atr_calculator.dataframe.columns
    assert "atr" in atr_calculator.dataframe.columns
    assert "prev_close" not in atr_calculator.dataframe.columns
