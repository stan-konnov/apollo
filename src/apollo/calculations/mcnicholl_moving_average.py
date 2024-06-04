import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class McNichollMovingAverageCalculator(BaseCalculator):
    """
    McNicholl Moving Average Calculator.

    McNicholl Moving Average is a variation of the Exponential Moving Average
    that uses a smoothing factor to calculate the weighted average of the data.

    Is an extension of the Double Exponential Moving Average (DEMA), therefore,
    the smoothing factor is calculated by dividing 2 by the window size plus 1,
    instead of regular Wilders smoothing factor of 1 / window size.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """Construct McNicholl Moving Average calculator."""

        super().__init__(dataframe, window_size)

        # Calculate the smoothing factor
        # by using the constant of two to achieve
        # double smoothing similar to the Double Exponential Moving Average
        self.smoothing_factor = 2 / (window_size + 1)

    def calculate_mcnicholl_moving_average(self) -> None:
        """Calculate McNicholl Moving Average."""

        # Calculate initial SMA
        simple_moving_average = (
            self.dataframe["adj close"]
            .rolling(window=self.window_size, min_periods=self.window_size)
            .mean()
        )

        # Calculate the weight for every data point
        weights = (1 - self.smoothing_factor) ** pd.Series(
            len(self.dataframe.index),
            index=self.dataframe.index,
        )

        # Reverse the weights so that the most
        # recent point gets the highest weight
        # achieving exponential smoothing
        weights = weights[::-1]

        # Apply the weights to the simple moving average
        weighted_close = simple_moving_average * self.smoothing_factor * weights

        # Calculate cumulative sum of weighted close prices
        close_cumulative_sum = weighted_close.cumsum()

        # Calculate cumulative sum of the weights
        weights_cumulative_sum = weights.cumsum()

        # Calculate the McNicholl Moving Average by dividing
        # the close cumulative sum by the weights cumulative sum
        mcnicholl_ma = close_cumulative_sum / weights_cumulative_sum

        # Finally, use the initial SMA values for the first N data points
        mcnicholl_ma[: self.window_size] = simple_moving_average[: self.window_size]

        # Preserve the McNicholl Moving Average on the dataframe
        self.dataframe["mnma"] = mcnicholl_ma
