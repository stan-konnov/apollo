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
        """
        Calculate McNicholl Moving Average.

        Try me in rolling window
        """

        # Initial SMA
        simple_moving_average = (
            self.dataframe["adj close"]
            .rolling(window=self.window_size, min_periods=self.window_size)
            .mean()
        )

        # Calculate the weights
        weights = (1 - self.smoothing_factor) ** pd.Series(
            len(self.dataframe.index),
            index=self.dataframe.index,
        )

        # Apply weights to the data
        weighted_data = self.dataframe["adj close"] * self.smoothing_factor * weights

        # Calculate the weighted cumulative sum in reverse order
        weighted_cumsum = weighted_data.expanding().sum()

        # Calculate the cumulative sum of the weights in reverse order
        weights_cumsum = weights.expanding().sum()

        # Calculate the McNicholl Moving Average
        mcnicholl_ma = weighted_cumsum / weights_cumsum

        # For initial period use SMA values
        mcnicholl_ma[: self.window_size] = simple_moving_average[: self.window_size]

        self.dataframe["mnma"] = mcnicholl_ma


"""
Here's a detailed explanation of the steps and why we reverse the series:

Calculate Weights:
The weights are calculated as (1 - alpha) ** pd.Series(range(len(data))), which gives a
decreasing series of weights from the start to the end of the data.

Reverse the Weights:
The weights are then reversed so that they start from the most recent point and decrease
going backwards. This reversal ensures that when applying the weights to the data, the
most recent point gets the highest weight.

Apply Weights:
The data is multiplied by these weights. By reversing the weighted data, we ensure that
the cumulative sum calculation considers the most recent data point first.

Calculate Cumulative Sums:

The weighted cumulative sum is calculated in reverse order to ensure that at each point,
we are summing up the contributions of all previous points, correctly weighted.
The cumulative sum of the weights is also calculated in reverse to normalize the
weighted sum.

Reverse Back:
The series is reversed back to its original order after the cumulative sums are computed
to align the weighted sums correctly with the original time series.

alpha = 2 / (window + 1) because it's akin to DAMA (Double Exponential Moving Average)
"""


def mcnicholl_moving_average(data: pd.Series, window: int) -> pd.Series:
    """
    Calculate the McNicholl Moving Average.

    :param data: Price data.
    :param window: Window size for the moving average.
    """
    alpha = 2 / (window + 1)
    sma = data.rolling(window=window, min_periods=1).mean()  # Initial SMA

    # Calculate the weights
    weights = (1 - alpha) ** pd.Series(range(len(data)))
    weights = weights[
        ::-1
    ]  # Reverse the weights so that the most recent point gets the highest weight

    # Apply weights to the data
    weighted_data: pd.Series = data * alpha * weights
    # Calculate the weighted cumulative sum in reverse order
    weighted_cumsum: pd.Series = weighted_data[::-1].expanding().sum()[::-1]
    # Calculate the cumulative sum of the weights in reverse order
    weights_cumsum = weights.expanding().sum()[::-1]

    # Calculate the McNicholl Moving Average
    mcnicholl_ma = weighted_cumsum / weights_cumsum

    # For initial period use SMA values
    mcnicholl_ma[:window] = sma[:window]

    return mcnicholl_ma
