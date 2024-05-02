from typing import ClassVar

import pandas as pd
from sklearn.base import BaseEstimator

# from sklearn.linear_model import Lasso, LinearRegression, Ridge
# from sklearn.model_selection import train_test_split
from apollo.calculations.base_calculator import BaseCalculator

"""
TODO: observable variable, X, can factor in all OHLC aspects
"""


class LinearRegressionModelCalculator(BaseCalculator):
    """
    Linear Regression Model Calculator.

    Since there are multiple linear regression models one can
    apply to given time series, this class acts as a model selector
    based on several statistical tests that quantify the goodness of fit.

    We apply two most commonly used metrics: R-squared and Mean Squared Error.
    The model with the highest R-squared and lowest MSE is used for rolling forecast.

    Linear regression models that we consider are:

    * Ordinary Least Squares (OLS)
    * Lasso Regression
    * Ridge Regression
    """

    # Stores selected model to apply
    # after running goodness of fit tests
    model_to_apply: ClassVar[BaseEstimator]

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct Linear Regression Model Calculator.

        :param dataframe: Dataframe to calculate ATR for.
        :param window_size: Window size for rolling ATR calculation.
        """

        super().__init__(dataframe, window_size)

    def _create_regression_trading_conditions(
        self,
        dataframe: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.Series]:
        """
        Create trading conditions to supply to the model.

        We consider our X variable to be the difference between
        the high and low, and open and close of every observation.

        We consider our Y variable to be the
        difference between close at T and close at T-1.
        """

        # Create a copy to avoid modifying original dataframe
        training_conditions_dataframe = dataframe.copy()

        # Calculate difference between high and low, open and close
        training_conditions_dataframe["high_low"] = dataframe["high"] - dataframe["low"]
        training_conditions_dataframe["open_close"] = (
            dataframe["open"] - dataframe["close"]
        )

        # Pack into dataframe
        x = training_conditions_dataframe[["open_close", "high_low"]]

        # Calculate Y variable
        y = dataframe["close"].shift(1) - dataframe["close"]

        return x, y
