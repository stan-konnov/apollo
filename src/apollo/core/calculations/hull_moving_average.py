import numpy as np
import pandas as pd

from apollo.core.calculations.base_calculator import BaseCalculator


class HullMovingAverageCalculator(BaseCalculator):
    """
    Hull Moving Average Calculator.

    Hull Moving Average is a weighted moving average
    designed by Alan Hull to reduce lag and increase
    responsiveness to short-term price movements.

    Calculation consists of three steps:

    1. Calculate WMA of the close using standard window size
    2. Calculate shorter WMA of the close using half window size
    3. Calculate HMA of the difference between two using square root of the window size

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    "The Hull Moving Average" Technical Analyst, (July-September 2010).
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """Construct Hull Moving Average Calculator."""

        super().__init__(dataframe, window_size)

    def calculate_hull_moving_average(self) -> None:
        """Calculate Hull Moving Average."""

        # Calculate weighed moving average of
        # the close using provided window size
        standard_window_wma = self._calculate_weighted_moving_average(
            self._dataframe["adj close"],
            self._window_size,
        )

        # Define a half window size
        # rounded down to the nearest integer
        half_window = self._window_size // 2

        # Calculate shorter weighed moving average
        # using half window size
        half_window_wma = self._calculate_weighted_moving_average(
            self._dataframe["adj close"],
            half_window,
        )

        # Calculate the difference between standard weighted moving average
        # and the shorter weighted moving average multiplied by 2
        # to emphasize shorter-term price movements
        wma_difference = 2 * half_window_wma - standard_window_wma

        # Take a square root of the window size
        # to make the Hull Moving Average even more responsive
        sqrt_window = int(np.sqrt(self._window_size))

        # Finally, calculate Hull Moving Average
        # over the difference using square root of the window size
        hull_moving_average = self._calculate_weighted_moving_average(
            wma_difference,
            sqrt_window,
        )

        # Write to the dataframe
        self._dataframe["hma"] = hull_moving_average

    def _calculate_weighted_moving_average(
        self,
        series: pd.Series,
        window_size: int,
    ) -> pd.Series:
        """
        Calculate Weighted Moving Average.

        :param series: Series to calculate WMA for.
        :param window_size: Window size for WMA calculation.
        :returns: Weighted moving average series.
        """

        # First, calculate range of equal weights (1, 2, ..., N)
        weights = np.arange(1, window_size + 1)

        # Then, calculate and return weighted moving average
        # by summing up the product of weights and series
        # and dividing it by sum of weights
        return series.rolling(window=window_size).apply(
            lambda x: np.sum(x * weights) / np.sum(weights),
            raw=True,
        )
