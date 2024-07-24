from typing import ClassVar

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from apollo.calculations.base_calculator import BaseCalculator


class LogisticRegressionModelCalculator(BaseCalculator):
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
        window_size: int,
    ) -> None:
        """
        Construct Logistic Regression Model Calculator.

        :param dataframe: Dataframe to model linear regression on.
        :param window_size: Size of the rolling window to forecast future periods.
        """

        super().__init__(dataframe, window_size)

        # NOTE: we use elasticnet penalty
        # with l1 ratio of 1.0 to enforce LASSO
        # regularization, and, thus, feature reduction
        # since we do not know beforehand which features are important
        self._model = LogisticRegression(
            penalty="elasticnet",
            solver="saga",
            l1_ratio=1.0,
        )

        # List of indices to expand the window
        self._expanding_indices: list[int] = []

    def forecast_periods(self) -> None:
        """Forecast future periods using logistic regression model."""

        # Reset the indices to allow for cleaner expanding window
        self._dataframe.reset_index(inplace=True)

        # Forecast future periods using rolling logistic regression
        self._dataframe["lrf"] = (
            self._dataframe["close"]
            .rolling(window=self._window_size)
            .apply(self._run_rolling_forecast)
        )

        # Reset indices back to date
        self._dataframe.set_index("date", inplace=True)

    def _run_rolling_forecast(self, series: pd.Series) -> float:
        """
        Run rolling forecast using logistic regression model.

        :param series: Series which is used for indexing out rolling window.
        :returns: Forecasted close for the next period.
        """

        # Get indices from the current window
        rolling_indices = series.index.to_list()

        # If expanding indices are empty
        # use indices from the current window
        if len(self._expanding_indices) == 0:
            self._expanding_indices = rolling_indices

        # Otherwise, append the last
        # index from the current window
        else:
            self._expanding_indices.append(rolling_indices[-1])

        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[self._expanding_indices]

        # Create trading conditions
        x, y = self._create_regression_trading_conditions(rolling_df)

        # Fit the model
        self._model.fit(x, y)

        # Forecast future periods
        return self._model.predict(x)[-1]

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
                dataframe["close"].shift(-1) > dataframe["close"],
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
