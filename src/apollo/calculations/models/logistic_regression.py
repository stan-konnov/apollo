import logging
from typing import ClassVar

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


class LogisticRegressionModelCalculator:
    """
    Logistic Regression Model Calculator.

    Logistic regression is a supervised method that is suitable for
    binary classification problems. It is used to model the probability of
    a certain class or event existing, such as, in our case, price going up or down.

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
        train_size: float,
    ) -> None:
        """
        Construct Logistic Regression Model Calculator.

        :param dataframe: Dataframe to model linear regression on.
        :param train_size: Size of the train set.

        NOTE: Logistic Regression Model Calculator does not require window size.
        """

        self.dataframe = dataframe
        self.train_size = train_size

    def forecast_periods(self) -> None:
        """
        Forecast future periods using logistic regression model.

        Create trading conditions, fit the model, and forecast future periods.
        """

        # Initialize the model
        model = LogisticRegression()

        # Create trading conditions
        x, y = self._create_regression_trading_conditions(self.dataframe)

        # Split into train and test
        x_train, x_test, y_train, y_test = self._create_train_split_group(x, y)

        # Fit the model
        model.fit(x_train, y_train)

        # Forecast future periods
        self.dataframe["lrf"] = model.predict(x)

    def _create_regression_trading_conditions(
        self,
        dataframe: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.Series]:
        """
        Create trading conditions to supply to the model.

        We consider our explanatory variable (X) to be the difference
        between all aspects of OHLC (open, high, low, close) of each observation.

        We consider our dependent variable (Y) to be a binary classifier
        that indicates whether the price will go up or down in the next period.

        :param dataframe: Dataframe to create trading conditions for.
        :returns: Explanatory variable (X) and dependent variable (Y).
        """

        # Create a copy to avoid modifying original dataframe
        training_conditions_dataframe = dataframe.copy()

        # Define explanatory variable (X)
        x = self._define_explanatory_variables(training_conditions_dataframe)

        # Calculate dependent variable (Y)
        y = pd.Series(
            np.where(
                self.dataframe["close"].shift(-1) > self.dataframe["close"],
                1,
                -1,
            ),
        )

        return x, y

    def _define_explanatory_variables(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Define explanatory variables for the model.

        As our explanatory variables, we consider the difference between
        all aspects of OHLC (open, high, low, close), amounting to 6 combinations:
        Open - High, Open - Low, Open - Close, High - Low, High - Close, Low - Close.

        Additionally, we consider the difference between Close and Adj Close.

        :param dataframe: Dataframe to calculate explanatory variables for.
        :returns: Dataframe with calculated differences between aspects.
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

    def _create_train_split_group(
        self,
        x: pd.DataFrame,
        y: pd.Series,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Create train and test split for given X and Y variables.

        :param x: explanatory variable.
        :param y: dependent variable.

        :returns: Train and test split.
        """

        # Split into train and test
        # NOTE: we do not shuffle, since:
        # our time series is already ordered by date
        # we want to forecast future values based on past values
        x_train, x_test, y_train, y_test = train_test_split(
            x,
            y,
            shuffle=False,
            train_size=self.train_size,
        )

        return x_train, x_test, y_train, y_test
