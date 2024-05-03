import logging
from typing import ClassVar

import pandas as pd
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from apollo.calculations.base_calculator import BaseCalculator

logger = logging.getLogger(__name__)

# Type hints exclusive to this class
ModelType = LinearRegression | Lasso | Ridge
ModelItem = tuple[str, ModelType]
ModelSpec = tuple[str, ModelType, float]

"""
Do we need regression output?
Can we just classify it?

Please make sure we know which model we're running (needs thinking through)
Ultimately, we want to have the model name in optimized parameters file
"""


class LinearRegressionModelCalculator(BaseCalculator):
    """
    Linear Regression Model Calculator.

    Since there are multiple linear regression models one can
    apply to given time series, this class acts as a model selector
    based on several statistical tests that quantify the goodness of fit.

    We apply two most commonly used metrics: R-squared and Mean Squared Error.
    The model with the highest R-squared and lowest MSE is used for forecasting.

    Linear regression models that we consider are:

    * Ordinary Least Squares (OLS)
    * Lasso Regression
    * Ridge Regression

    Donadio and Ghosh, Algorithmic Trading, 2019, 1st ed.
    """

    # Mapping of OHLC short names to their respective names
    # Used in creating explanatory variables for the model
    ohlc_aspects: ClassVar[dict[str, str]] = {
        "o": "open",
        "h": "high",
        "l": "low",
        "c": "close",
        "a": "adj close",
    }

    # Combinations of OHLC aspects to calculate differences between
    # Used in creating explanatory variables for the model
    ohlc_aspects_combinations: ClassVar[list[tuple[str, str]]] = [
        ("o", "h"),
        ("o", "l"),
        ("o", "c"),
        ("h", "l"),
        ("h", "c"),
        ("l", "c"),
        ("c", "a"),
    ]

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
        split_ratio: float,
        smoothing_factor: float,
    ) -> None:
        """
        Construct Linear Regression Model Calculator.

        :param dataframe: Dataframe to calculate ATR for.
        :param window_size: Window size for rolling ATR calculation.
        :param split_ratio: Ratio to split data into train and test.
        """
        super().__init__(dataframe, window_size)

        self.split_ratio = split_ratio
        self.smoothing_factor = smoothing_factor

    def forecast_periods(self) -> None:
        """
        Forecast future periods using one of the linear regression models.

        Select the model with the highest R-squared and lowest Mean Squared Error.

        Create trading conditions and predict future periods.
        """

        # Select the model for forecasting
        # NOTE: we do not need to store the model,
        # since we parametrize smoothing factor and split ratio
        # Therefore, each backtesting run might end up using different model
        model_item = self._select_model_to_use()

        model = model_item[1]

        # Create trading conditions
        x, _ = self._create_regression_trading_conditions(self.dataframe)

        # Drop first row, to accommodate for T-1 close shift
        self.dataframe.drop(self.dataframe.index[0], inplace=True)

        # Forecast future periods
        self.dataframe["forecast"] = model.predict(x)

    def _select_model_to_use(self) -> ModelSpec:
        """
        Select model to use based on R-squared and Mean Squared Error.

        Fit, predict and score all models.
        Select the model with the highest score.

        :return: Model specification with the highest score.
        """

        models: list[ModelItem] = [
            ("OLS", LinearRegression()),
            ("Lasso", Lasso(alpha=self.smoothing_factor)),
            ("Ridge", Ridge(alpha=self.smoothing_factor)),
        ]

        model_specs: list[ModelSpec] = []

        for model_item in models:
            model_spec = self._fit_predict_score(model_item)
            model_specs.append(model_spec)

        return max(model_specs, key=lambda x: x[2])

    def _fit_predict_score(self, model_item: ModelItem) -> ModelSpec:
        """
        Fit the model, predict on both train and test data, and score the model.

        For every provided model, split the data into train and test, fit, predict
        and gauge the model's performance based on R-squared and Mean Squared Error.

        Apply the scoring heuristic on train and test metrics to select the best model.

        :param model_item: Tuple containing model name and model instance.
        :returns: Tuple containing model name, model instance and model score.
        """

        # Unpack model item
        name, model = model_item

        # Create trading conditions
        x, y = self._create_regression_trading_conditions(self.dataframe)

        # Split into train and test
        x_train, x_test, y_train, y_test = self._create_train_split_group(x, y)

        # Fit the model
        model.fit(x_train, y_train)

        # Predict and gauge metrics on train data
        forecast_train = model.predict(x_train)
        r_squared_train = r2_score(y_train, forecast_train)
        mean_square_error_train = mean_squared_error(y_train, forecast_train)

        # Predict and gauge metrics on test data
        forecast_test = model.predict(x_test)
        r_squared_test = r2_score(y_test, forecast_test)
        mean_square_error_test = mean_squared_error(y_test, forecast_test)

        # Score the model
        model_score = self._score_model(
            r_squared_train=float(r_squared_train),
            mean_square_error_train=float(mean_square_error_train),
            r_squared_test=float(r_squared_test),
            mean_square_error_test=float(mean_square_error_test),
        )

        # Return model specification
        return name, model, model_score

    def _create_regression_trading_conditions(
        self,
        dataframe: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.Series]:
        """
        Create trading conditions to supply to the model.

        We consider our explanatory variable (X) to be the difference
        between all aspects of OHLC (open, high, low, close) of each observation.

        We consider our dependent variable (Y) to be the difference
        between close at T and close at T-1.

        :param dataframe: Dataframe to create trading conditions for.
        :return: Explanatory variable (X) and dependent variable (Y).
        """

        # Create a copy to avoid modifying original dataframe
        training_conditions_dataframe = dataframe.copy()

        # Define explanatory variable (X)
        x = self._define_explanatory_variables(training_conditions_dataframe)

        # Calculate dependent variable (Y)
        y = dataframe["close"].shift(1) - dataframe["close"]

        # Remove row from X and Y where
        # Y is NaN after shift and drop NaN from Y
        x = x.drop(x.index[0])
        y.dropna(inplace=True)

        return x, y

    def _define_explanatory_variables(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Define explanatory variables for the model.

        As our explanatory variables, we consider the difference between
        all aspects of OHLC (open, high, low, close), amounting to 6 combinations:
        Open - High, Open - Low, Open - Close, High - Low, High - Close, Low - Close.

        Additionally, we consider the difference between Close and Adj Close.

        :param dataframe: Dataframe to calculate explanatory variables for.
        :return: Dataframe with calculated differences between aspects.
        """

        variables_to_apply = []

        # Loop through all combinations and calculate differences
        for aspect_a, aspect_b in self.ohlc_aspects_combinations:
            dataframe[f"{aspect_a}_{aspect_b}"] = (
                dataframe[self.ohlc_aspects[aspect_a]]
                - dataframe[self.ohlc_aspects[aspect_b]]
            )

            # Append to list of columns to
            # index out from resulting dataframe
            variables_to_apply.append(f"{aspect_a}_{aspect_b}")

        # Return only the columns we are interested in
        return dataframe[variables_to_apply]

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
