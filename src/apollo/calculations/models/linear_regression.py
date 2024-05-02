from typing import ClassVar

import pandas as pd
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from apollo.calculations.base_calculator import BaseCalculator

"""
TODO: observable variable, X, can factor in all OHLC aspects
TODO: add logging for MSE and R2 for each model

How do you know that model with best
fit will be best at producing signals?
Consider backtesting on top, and if backtesting
results are different, then scrap statistical tests
"""

# Type hints exclusive to this class
ModelType = LinearRegression | Lasso | Ridge
ModelItem = tuple[str, ModelType]
ModelSpec = tuple[str, ModelType, float]


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

    Donadio and Ghosh, Algorithmic Trading, 2019, 1st ed.
    """

    # List of models to choose from
    # Represents model name, model instance, model score
    models_to_apply: ClassVar[list[ModelSpec]]

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

    def select_best_model(self) -> ModelSpec:
        """
        Select best model.

        And write a better docstring.
        """

        models: list[ModelItem] = [
            ("OLS", LinearRegression()),
            # Use smoothing factors of 0.1 and 10000
            # Donadio and Ghosh, Algorithmic Trading, 2019, p.98
            ("Lasso", Lasso(alpha=0.1)),
            ("Ridge", Ridge(alpha=0.1)),
        ]

        model_specs: list[ModelSpec] = []

        for model_item in models:
            # print(model_item[0])

            model_spec = self._fit_predict_score(model_item)
            model_specs.append(model_spec)

        return max(model_specs, key=lambda x: x[2])

    def _fit_predict_score(self, model_item: ModelItem) -> ModelSpec:
        """
        Fit the model, predict on both train and test data, and score the model.

        Please write more, brotha.
        """

        name, model = model_item

        x, y = self._create_regression_trading_conditions(self.dataframe)

        x_train, x_test, y_train, y_test = self._create_train_split_group(x, y)

        model.fit(x_train, y_train)

        forecast_train = model.predict(x_train)
        r_squared_train = r2_score(y_train, forecast_train)
        mean_square_error_train = mean_squared_error(y_train, forecast_train)

        forecast_test = model.predict(x_test)
        r_squared_test = r2_score(y_test, forecast_test)
        mean_square_error_test = mean_squared_error(y_test, forecast_test)

        model_score = self._score_model(
            r_squared_train=float(r_squared_train),
            mean_square_error_train=float(mean_square_error_train),
            r_squared_test=float(r_squared_test),
            mean_square_error_test=float(mean_square_error_test),
        )

        # print("R-squared train:", r_squared_train)
        # print("Mean square error train:", mean_square_error_train)
        # print("R-squared test:", r_squared_test)
        # print("Mean square error test:", mean_square_error_test)

        return name, model, model_score

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
        x = x.drop(x.index[0])
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
        r_squared_train: float,
        mean_square_error_train: float,
        r_squared_test: float,
        mean_square_error_test: float,
    ) -> float:
        """
        Score the model based on mean square error and R-squared.

        Sum R-squared and return the factor.
        (We want to maximize R-squared, hence the positive sign).

        Sum mean square error and multiply by -1 to get the factor.
        (We want to minimize MSE, hence the negative sign).

        Sum both factors to get the final score.

        NOTE: this is a simple heuristic to select the best model.
        It can and will produce negative values, but we are not interested
        in those values (yet), we are interested in the model with the highest score.

        :param r_squared_train: R-squared for train data.
        :param mean_square_error_train: Mean square error for train data.
        :param r_squared_test: R-squared for test data.
        :param mean_square_error_test: Mean square error for test data.
        :return: Score of the model.
        """

        r_squared_factor = r_squared_train + r_squared_test

        mean_square_error_factor = (
            mean_square_error_train + mean_square_error_test
        ) * -1

        return r_squared_factor + mean_square_error_factor
