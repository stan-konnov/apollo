import numpy as np
import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class SwingMomentsCalculator(BaseCalculator):
    """
    Swings Moments Calculator.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(
            self,
            dataframe: pd.DataFrame,
            window_size: int,
            swing_filter: float,
        ) -> None:
        """
        Construct Swing Moments calculator.

        :param dataframe: Dataframe to calculate swings for.
        :param window_size: Window size for rolling swing moment calculation.
        :param swing_filter: Swing filter for determining swing highs and lows.
        """

        super().__init__(dataframe, window_size)

        self.swing_l = 0.0
        self.swing_h = 0.0
        self.in_downswing = False
        self.swing_filter = swing_filter
        self.swing_moments: list[float] = []


    def calculate_swing_moments(self) -> None:
        """Calculate rolling swing moments."""

        # Record the low of the first bar (before rolling window) as the swing low
        self.swing_l = self.dataframe.iloc[self.window_size - 2]["low"]

        # Record the high of the first bar (before rolling window) as swing high
        self.swing_h = self.dataframe.iloc[self.window_size - 2]["high"]

        # Following the swing high, assume we are in downswing
        # Kaufman, TSM, p. 168
        self.in_downswing = True

        # Fill swing moments array with N NaN, where N = window size
        self.swing_moments = np.full(
            (1, self.window_size - 1),
            np.nan,
        ).flatten().tolist()

        # Calculate swings
        self.dataframe["adj close"].rolling(self.window_size).apply(
            self.__calc_sm, args=(self.dataframe, ),
        )

        # Write swings to the dataframe
        self.dataframe["sm"] = self.swing_moments


    def __calc_sm(self, series: pd.Series, dataframe: pd.DataFrame) -> float:
        """
        Calculate rolling swings for a given window.

        :param series: Series which is used for indexing out rolling window.
        :param dataframe: Original dataframe acting as a source of rolling window.
        :returns: Dummy float to satisfy Pandas' return value.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = dataframe.loc[series.index]

        # Grab current low
        current_low = rolling_df.iloc[-1]["low"]

        # Grab current high
        current_high = rolling_df.iloc[-1]["high"]

        # Calculate current swing filter
        current_swing_filter = rolling_df.iloc[-1]["adj close"] * self.swing_filter

        # If we are in downswing
        if self.in_downswing:

            # Test if downswing continues
            if current_low < self.swing_l:

                # Treat current low as new swing low
                self.swing_l = current_low

            # Test if downswing reverses
            if current_high - self.swing_l > current_swing_filter:

                # If so, we have an upswing
                self.in_downswing = False

                # Treat current low as new swing low
                self.swing_l = current_low

                # Treat current high as new swing high
                self.swing_h = current_high

                # Add positive float to the list
                self.swing_moments.append(1.0)

                # Return dummy float
                return 0.0

            # Append falsy float as it is a continuation
            self.swing_moments.append(0.0)

            # Return dummy float
            return 0.0

        # Otherwise, we are in upswing

        # Test if upswing continues
        if current_high > self.swing_h:

            # Treat current high as new swing high
            self.swing_h = current_high

        # Test if upswing reverses
        if self.swing_h - current_low > current_swing_filter:

            # If so, we have downswing
            self.in_downswing = True

            # Append negative float to the list
            self.swing_moments.append(-1.0)

            # Return dummy float
            return 0.0

        # Append falsy float as it is a continuation
        self.swing_moments.append(0.0)

        # Return dummy float
        return 0.0
