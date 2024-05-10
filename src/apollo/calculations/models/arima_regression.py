import pandas as pd
from statsmodels.tsa.arima.model import ARIMA, ARIMAResults
from statsmodels.tsa.seasonal import seasonal_decompose

from apollo.calculations.base_calculator import BaseCalculator

"""
TODO:

1. Look into SARIMA.

2. Apply Kalman Filter (from Kaufman).

3. Look into seasonal_decompose.

4. Move transformer here.

5. Auto ARIMA: (auto_arima),

    The auto_arima function returns a fitted ARIMA model
    after determining the most optimal p, d, q parameters.

https://www.analyticsvidhya.com/blog/2021/07/stock-market-forecasting-using-time-series-analysis-with-arima-model/
"""


class ARIMARegressionModelCalculator(BaseCalculator):
    """
    ARIMA Regression Model Calculator.

    (Auto Regressive Integrated Moving Average).

    ARIMA is a regression model that predicts future values
    based solely on the past values of the same time series.

    Therefore, due to the lack of explanatory variables,
    ARIMA requires the time series to be stationary.

    (Please refer to Time Series Transformer for more information).

    ARIMA operates on three parameters:

    * p: The number of lag observations included in the model.
    * d: The number of times that the raw observations are differenced.
    * q: The size of the moving average window.

    Donadio and Ghosh, Algorithmic Trading, 2019, 1st ed.
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """Construct ARIMA Regression Model Calculator.."""
        super().__init__(dataframe, window_size)

    def forecast_periods(self) -> None:
        """
        Forecast future periods using ARIMA regression model.

        Stationarize the time series, fit the model, and forecast future periods.
        """

        time_series = seasonal_decompose(
            self.dataframe["adj close"],
            model="multiplicative",
            period=self.window_size,
        )

        # Params to be computed, WIP
        model = ARIMA(time_series.trend, order=(5, 0, 5))

        results: ARIMAResults = model.fit()

        self.dataframe["arf"] = results.fittedvalues

        # forecast: pd.Series = fitted_model.forecast(steps=self.dataframe.shape[0])
        # forecast.index = self.dataframe.index
        # self.dataframe["arf"] = forecast

        # forecast(steps=1) in a rolling window!
        # Are we training on the entire dataset?
        # Or are we training on a rolling window?
