import pandas as pd
from statsmodels.tsa.stattools import adfuller


class TimeSeriesTransformer:
    """
    Time Series Transformer.

    Prepares time series for forecasting by removing
    trends and seasonality making the time series stationary.

    The stationarity of time series implies that the statistical
    properties, such as mean, variance, and autocorrelation, do not change over time.

    No (auto) regression analysis can be performed on non-stationary
    time series, as it can lead to spurious regression results.

    Granger, Newbold, Journal of Econometrics, 1974.
    """

    # Threshold for p-value to determine stationarity
    P_VALUE_THRESHOLD: float = 0.05

    @classmethod
    def bring_to_stationary(cls, time_series: pd.Series) -> pd.Series:
        """
        Make time series stationary.

        There are multiple ways to making time series stationary
        yet, the most commonly used is differencing.
        """

        # We first apply Augmented Dickey-Fuller test
        # to check for stationarity in the time series
        # where non-stationarity exists if p-value > 0.05
        adf_test = adfuller(time_series, autolag="AIC")

        # And if the time series is non-stationary,
        # we apply differencing to make it stationary
        if adf_test[1] > cls.P_VALUE_THRESHOLD:
            time_series = time_series.diff()

        return time_series
