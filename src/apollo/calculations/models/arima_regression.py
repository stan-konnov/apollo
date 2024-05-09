import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

from apollo.calculations.base_calculator import BaseCalculator
from apollo.utils.time_series_transformer import TimeSeriesTransformer

"""Look into SARIMAX."""


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

    * q: The size of the moving average window.
    * p: The number of lag observations included in the model.
    * d: The number of times that the raw observations are differenced.

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

        # Stationarize the time series
        time_series = TimeSeriesTransformer.bring_to_stationary(self.dataframe["close"])

        # Params to be computed, WIP
        model = ARIMA(time_series, order=(2, 0, 2))

        self.dataframe["arf"] = model.fit()
