import pandas as pd
import pytest
from statsmodels.tsa.arima.model import ARIMA, ARIMAResults
from statsmodels.tsa.seasonal import seasonal_decompose

from apollo.calculations.models.arima_regression import ARIMARegressionModelCalculator


@pytest.mark.usefixtures("dataframe", "window_size")
def test__forecast_trend_periods__for_correct_columns(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test forecast_trend_periods method for correct columns.

    Resulting dataframe must have "artf" column.
    """

    arf_calculator = ARIMARegressionModelCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    arf_calculator.forecast_trend_periods()

    assert "artf" in dataframe.columns


@pytest.mark.usefixtures("dataframe", "window_size")
def test__forecast_trend_periods__for_correct_forecast(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test forecast_trend_periods method for correct trend forecast.

    Resulting forecast must be a correct forecast of the model.
    """

    control_dataframe = dataframe.copy()
    control_dataframe.reset_index(inplace=True)

    control_dataframe["artf"] = (
        control_dataframe["adj close"]
        .rolling(
            window=window_size,
        )
        .apply(
            _run_rolling_forecast,
        )
    )

    control_dataframe.set_index("date", inplace=True)

    arm_calculator = ARIMARegressionModelCalculator(
        dataframe=dataframe,
        window_size=window_size,
    )

    arm_calculator.forecast_trend_periods()

    pd.testing.assert_series_equal(dataframe["artf"], control_dataframe["artf"])


def _run_rolling_forecast(series: pd.Series) -> float:
    """
    Mimicry of rolling ARIMA forecast for testing purposes.

    Please see ARIMARegressionModelCalculator for detailed explanation.
    """

    time_series = seasonal_decompose(
        series,
        model="multiplicative",
        period=1,
        two_sided=False,
    )

    model = ARIMA(time_series.trend, order=(1, 1, 1))

    results: ARIMAResults = model.fit()

    forecast: pd.Series = results.forecast(steps=1)

    return forecast.iloc[0]
