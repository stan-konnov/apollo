from typing import ClassVar

import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

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

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
        split_ratio: float,
    ) -> None:
        """
        Construct Linear Regression Model Calculator.

        :param dataframe: Dataframe to calculate ATR for.
        :param window_size: Window size for rolling ATR calculation.
        :param split_ratio: Ratio to split data into train and test.
        """

        super().__init__(dataframe, window_size)

        self.split_ratio = split_ratio

    def fit_and_predict(self) -> None:
        """
        Fit the model to the training data.

        Create trading conditions and split into train and test.
        """

        x, y = self._create_regression_trading_conditions(self.dataframe)

        x_train, x_test, y_train, y_test = self.create_train_split_group(x, y)

        ordinary_least_squares = LinearRegression()
        ordinary_least_squares.fit(x_train, y_train)

        forecast = ordinary_least_squares.predict(x_train)

        variance_score = r2_score(y_train, forecast)
        mse_score = mean_squared_error(y_train, forecast)

        print("MSE Train: ", mse_score)
        print("Variance Train: ", variance_score)

        forecast = ordinary_least_squares.predict(x_test)

        variance_score = r2_score(y_test, forecast)
        mse_score = mean_squared_error(y_test, forecast)

        print("MSE Test: ", mse_score)
        print("Variance Test: ", variance_score)

    def _create_regression_trading_conditions(
        self,
        dataframe: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.Series]:
        """
        Create trading conditions to supply to the model.

        We consider our explanatory variable (X) to be the difference
        between the high and low, and open and close of every observation.

        We consider our dependent variable (Y) to be the difference
        between close at T and close at T-1.
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

        # Remove row from X and Y where
        # Y is NaN after shift and drop NaN from Y
        x.drop(x.index[0], inplace=True)
        y.dropna(inplace=True)

        return x, y

    def create_train_split_group(self, x: pd.DataFrame, y: pd.Series) -> tuple:
        """
        Create train and test split for given X and Y variables.

        :param x: explanatory variable.
        :param y: dependent variable.

        :return: Train and test split.
        """

        # Split into train and test
        # NOTE: we do not shuffle, since:
        # our time series is already ordered by date
        # we want to forecast future values based on past values
        x_train, x_test, y_train, y_test = train_test_split(
            x,
            y,
            shuffle=False,
            test_size=self.split_ratio,
        )

        return x_train, x_test, y_train, y_test
