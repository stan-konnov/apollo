import pandas as pd

from apollo.calculators.base_calculator import BaseCalculator


class DistributionMomentsCalculator(BaseCalculator):
    """
    Distribution Moments Calculator.

    Calculates rolling distribution moments such as
    mean, standard deviation, skewness, kurtosis, and z-score.
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct Distribution Moments Calculator.

        :param dataframe: Dataframe to calculate distribution moments for.
        :param window_size: Window size for rolling distribution moments calculation.
        """

        super().__init__(dataframe, window_size)

    def calculate_distribution_moments(self) -> None:
        """Calculate rolling distribution moments."""

        # Get rolling window object to calculate distribution moments
        rolling_window = self._dataframe["adj close"].rolling(window=self._window_size)

        # Calculate rolling average
        self._dataframe["avg"] = rolling_window.mean()

        # Calculate rolling standard deviation
        self._dataframe["std"] = rolling_window.std()

        # Calculate rolling skewness
        self._dataframe["skew"] = rolling_window.skew()

        # Calculate rolling kurtosis
        self._dataframe["kurt"] = rolling_window.kurt()

        # Calculate rolling z-score from mean and standard deviation
        self._dataframe["z_score"] = (
            self._dataframe["adj close"] - self._dataframe["avg"]
        ) / self._dataframe["std"]
