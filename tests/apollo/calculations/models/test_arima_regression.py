import pandas as pd
import pytest
from statsmodels.tsa.arima.model import ARIMA, ARIMAResults
from statsmodels.tsa.seasonal import seasonal_decompose

from apollo.calculations.models.arima_regression import ARIMARegressionModelCalculator

TRAIN_SIZE = 0.4


@pytest.mark.usefixtures("dataframe", "window_size")
def test__forecast_periods__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test forecast_periods method for correct columns.

    Resulting dataframe must have "artf" column.
    """

    arf_calculator = ARIMARegressionModelCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    arf_calculator.forecast_periods()

    assert "artf" in arf_calculator.dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__forecast_periods__for_correct_forecast(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test forecast_periods method for correct trend forecast.

    Resulting forecast must be a correct forecast of the model.
    """

    control_dataframe = dataframe.copy()
    control_dataframe.reset_index(inplace=True)

    control_time_series = seasonal_decompose(
        control_dataframe["adj close"],
        model="multiplicative",
        period=window_size,
    )

    model = ARIMA(
        control_time_series.trend,
        order=(window_size, window_size, window_size),
    )

    control_results: ARIMAResults = model.fit()
    control_dataframe["artf"] = control_results.fittedvalues

    control_dataframe.set_index("date", inplace=True)

    arm_calculator = ARIMARegressionModelCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    arm_calculator.forecast_periods()

    pd.testing.assert_series_equal(dataframe["artf"], control_dataframe["artf"])
