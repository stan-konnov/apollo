import warnings

import pandas as pd
from statsmodels.tools.sm_exceptions import ConvergenceWarning
from statsmodels.tsa.arima.model import ARIMA, ARIMAResults
from statsmodels.tsa.seasonal import seasonal_decompose

from apollo.calculations.base_calculator import BaseCalculator

warnings.simplefilter("ignore", ConvergenceWarning)


class ARIMARegressionModelCalculator(BaseCalculator):
    """
    ARIMA Regression Model Calculator.

    (Auto Regressive Integrated Moving Average).

    ARIMA is a regression model that predicts future values
    based solely on the past values of the same time series.

    ARIMA operates on three parameters:

    * p: The number of lag observations included in the model.
    * d: The number of times that the raw observations are differenced.
    * q: The size of the moving average window.

    For more insights on differencing, please refer to the concept
    of stationarity vs non-stationarity of time series.

    Most common approaches to finding the optimal parameters are:

    * ACF: Auto Correlation Function.
    * PACF: Partial Auto Correlation Function.

    Yet, after running experiments with different datasets and parameters,
    it has been discovered that the optimal parameters specifically
    for our case equal one observation for each parameter.

    Additionally, it has been discovered that forecasting the prices
    of the time series is not the best approach, backtesting wise.

    Instead, we forecast the trend of the time series
    and incorporate it into our trading strategy.

    Donadio and Ghosh, Algorithmic Trading, 2019, 1st ed.
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """Construct ARIMA Regression Model Calculator.."""

        super().__init__(dataframe, window_size)

    def forecast_trend_periods(self) -> None:
        """Forecast trend periods using ARIMA regression model."""

        # Reset the indices to integer values
        # to avoid issues with the ARIMA model
        self.dataframe.reset_index(inplace=True)

        # Forecast the trend component
        # using rolling ARIMA regression
        self.dataframe["artf"] = (
            self.dataframe["adj close"]
            .rolling(window=self.window_size)
            .apply(self._run_rolling_forecast)
        )

        # Reset indices back to date
        self.dataframe.set_index("date", inplace=True)

    def _run_rolling_forecast(self, series: pd.Series) -> float:
        """Run rolling forecast using ARIMA regression model."""

        # Decompose the time series into
        # trend, seasonal, and residual components within the
        # period of one observation (since we are forecasting one period)
        time_series = seasonal_decompose(
            series,
            model="multiplicative",
            period=1,
            two_sided=False,
        )

        # Create ARIMA model for the trend component with
        # one lag observation, one differencing, and one moving average
        model = ARIMA(time_series.trend, order=(1, 1, 1))

        # Fit the model and gauge the results
        results: ARIMAResults = model.fit()

        # Return out of sample forecast
        return results.forecast(steps=1)
