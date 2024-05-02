from typing import ClassVar

import pandas as pd
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from apollo.calculations.base_calculator import BaseCalculator

"""
TODO: observable variable, X, can factor in all OHLC aspects
"""

ModelType = LinearRegression | Lasso | Ridge
ModelsScore = tuple[tuple[float, float], tuple[float, float]]
ModelsToApply = tuple[str, ModelType, ModelsScore]


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

    # Tuple of models to choose from
    # Represents model name, model instance, model score
    models_to_apply: ClassVar[ModelsToApply]

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

    def fit_predict_score(self) -> None:
        """
        Fit the model, predict on both train and test data, and score the model.

        Create trading conditions and split into train and test.
        """

        x, y = self._create_regression_trading_conditions(self.dataframe)

        x_train, x_test, y_train, y_test = self._create_train_split_group(x, y)

        ordinary_least_squares = LinearRegression()
        ordinary_least_squares.fit(x_train, y_train)

        forecast_train = ordinary_least_squares.predict(x_train)
        variance_train = r2_score(y_train, forecast_train)
        mce_train = mean_squared_error(y_train, forecast_train)

        forecast_test = ordinary_least_squares.predict(x_test)
        variance_test = r2_score(y_test, forecast_test)
        mse_test = mean_squared_error(y_test, forecast_test)

        # model_score = self._score_model(
        #     train_mean_square_error=mce_train,
        #     train_r_squared=variance_train,
        #     test_mean_square_error=test_mse,
        #     test_r_squared=test_variance,
        # )

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

    def _create_train_split_group(self, x: pd.DataFrame, y: pd.Series) -> tuple:
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

    def _score_model(
        self,
        train_r_squared: float,
        train_mean_square_error: float,
        test_r_squared: float,
        test_mean_square_error: float,
    ) -> float:
        """
        Score the model based on mean square error and R-squared.

        Sum R-squared and return the factor.
        (We want to maximize R-squared, hence the positive sign).

        Sum mean square error and multiply by -1 to get the factor.
        (We want to minimize MSE, hence the negative sign).

        Sum both factors to get the final score.

        :param train_r_squared: R-squared for train data.
        :param train_mean_square_error: Mean square error for train data.
        :param test_r_squared: R-squared for test data.
        :param test_mean_square_error: Mean square error for test data.
        :return: Score of the model.
        """

        r_squared_factor = train_r_squared + test_r_squared

        mean_square_error_factor = (
            train_mean_square_error + test_mean_square_error
        ) * -1

        return r_squared_factor + mean_square_error_factor
