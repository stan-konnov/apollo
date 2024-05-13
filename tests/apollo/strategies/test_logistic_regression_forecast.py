import pandas as pd
import pytest

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.models.logistic_regression import (
    LogisticRegressionModelCalculator,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.logistic_regression_forecast import LogisticRegressionForecast

TRAIN_SIZE = 0.4


@pytest.mark.usefixtures("dataframe", "window_size")
def test__logistic_regression_forecast__with_valid_parameters(
    dataframe: pd.DataFrame,
    window_size: int,
) -> None:
    """
    Test Logistic Regression Forecast with valid parameters.

    Strategy should properly calculate trading signals.
    """

    control_dataframe = dataframe.copy()
    control_dataframe["signal"] = 0

    atr_calculator = AverageTrueRangeCalculator(control_dataframe, window_size)
    atr_calculator.calculate_average_true_range()

    lrm_calculator = LogisticRegressionModelCalculator(
        dataframe=control_dataframe,
        train_size=TRAIN_SIZE,
    )
    lrm_calculator.forecast_periods()

    control_dataframe.loc[control_dataframe["lrf"] > 0, "signal"] = LONG_SIGNAL
    control_dataframe.loc[control_dataframe["lrf"] < 0, "signal"] = SHORT_SIGNAL

    control_dataframe.dropna(inplace=True)

    logistic_regression_forecast = LogisticRegressionForecast(
        dataframe=dataframe,
        window_size=window_size,
        train_size=TRAIN_SIZE,
    )

    logistic_regression_forecast.model_trading_signals()

    pd.testing.assert_series_equal(dataframe["signal"], control_dataframe["signal"])
