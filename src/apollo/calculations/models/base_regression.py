import pandas as pd
from statsmodels.tsa.stattools import adfuller


class BaseRegressionModelCalculator:
    """
    Base class for all regression models.

    Prepares time series for forecasting by removing
    trends and seasonality making the time series stationary.

    The stationarity of time series implies that the statistical
    properties, such as mean, variance, and autocorrelation, do not change over time.

    No regression analysis can be performed on non-stationary time series,
    as it can lead to spurious regression results.

    Granger, Newbold, Journal of Econometrics, 1974.
    """

    # Threshold for p-value to determine stationarity
    P_VALUE_THRESHOLD: float = 0.05

    def __init__(self, dataframe: pd.DataFrame) -> None:
        """
        Construct Base Regression Model.

        :param dataframe: Dataframe with price data.
        """

        self.transformed_dataframe = dataframe.copy()

    def _bring_to_stationary(self) -> None:
        """
        Make time series stationary.

        There are multiple ways to make time series stationary, yet,
        the most applicable to our case is seasonal differencing,
        as it takes care of both trend and seasonality.
        """

        # We first apply Augmented Dickey-Fuller test
        # to check for stationarity in the time series
        # where non-stationarity exists if p-value > 0.05
        adf_test = adfuller(
            self.transformed_dataframe["close"],
            autolag="AIC",
        )

        if adf_test[1] > self.P_VALUE_THRESHOLD:
            # Differentiate all aspects of OHLCV
            # (all columns except for the ticker)
            self.transformed_dataframe = self.transformed_dataframe.loc[
                :,
                self.transformed_dataframe.columns != "ticker",
            ].diff()

            # Drop the first row with NaN values
            self.transformed_dataframe.drop(
                self.transformed_dataframe.index[0],
                inplace=True,
            )
