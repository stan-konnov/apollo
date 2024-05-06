import pandas as pd
import pytest

from apollo.calculations.models.linear_regression import LinearRegressionModelCalculator

SPLIT_RATIO = 0.6
SMOOTHING_FACTOR = 0.1


@pytest.mark.usefixtures("dataframe", "window_size")
def test__forecast_periods__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test forecast_periods method for correct columns.

    Resulting dataframe must have "lrf" column.
    """

    lrm_calculator = LinearRegressionModelCalculator(
        dataframe=dataframe,
        window_size=window_size,
        split_ratio=SPLIT_RATIO,
        smoothing_factor=SMOOTHING_FACTOR,
    )

    lrm_calculator.forecast_periods()

    assert "lrf" in lrm_calculator.dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__forecast_periods__for_correctly_dropping_first_observation(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test forecast_periods method for correctly dropping first observation.

    Resulting dataframe length must be equal to the original dataframe length -1.
    """

    control_dataframe_length = len(dataframe.copy().index)

    lrm_calculator = LinearRegressionModelCalculator(
        dataframe=dataframe,
        window_size=window_size,
        split_ratio=SPLIT_RATIO,
        smoothing_factor=SMOOTHING_FACTOR,
    )

    lrm_calculator.forecast_periods()

    assert len(dataframe.index) == control_dataframe_length - 1
