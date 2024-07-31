import numpy as np
import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class SwingEventsCalculator(BaseCalculator):
    """
    Swings Events Calculator.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    # Constant to represent upswing
    UP_SWING: float = 1.0

    # Constant to represent downswing
    DOWN_SWING: float = -1.0

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
        swing_filter: float,
    ) -> None:
        """
        Construct Swing Events calculator.

        :param dataframe: Dataframe to calculate swings for.
        :param window_size: Window size for rolling swing events calculation.
        :param swing_filter: Swing filter for determining swing highs and lows.
        """

        super().__init__(dataframe, window_size)

        self._swing_l = 0.0
        self._swing_h = 0.0

        self._in_downswing = False
        self._swing_filter = swing_filter

        self._swing_events: list[float] = []

    def calculate_swing_events(self) -> None:
        """Calculate rolling swing events."""

        # Record the low of the first bar (before rolling window) as swing low
        self._swing_l = self._dataframe.iloc[self._window_size - 2]["adj low"]

        # Record the high of the first bar (before rolling window) as swing high
        self._swing_h = self._dataframe.iloc[self._window_size - 2]["adj high"]

        # Following the swing high, assume we are in downswing
        # Kaufman, TSM, p. 168
        self._in_downswing = True

        # Fill swing events array with N NaN, where N = window size
        self._swing_events = (
            np.full((1, self._window_size - 1), np.nan).flatten().tolist()
        )

        # Calculate swings
        self._dataframe["adj close"].rolling(self._window_size).apply(self._calc_se)

        # Write swings to the dataframe
        self._dataframe["se"] = self._swing_events

    def _calc_se(self, series: pd.Series) -> float:
        """
        Calculate rolling swings for a given window.

        :param series: Series which is used for indexing out rolling window.
        :param dataframe: Original dataframe acting as a source of rolling window.
        :returns: Dummy float to satisfy Pandas' return value.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[series.index]

        # Grab current low
        current_low = rolling_df.iloc[-1]["adj low"]

        # Grab current high
        current_high = rolling_df.iloc[-1]["adj high"]

        # Calculate current swing filter
        current_swing_filter = rolling_df.iloc[-1]["adj close"] * self._swing_filter

        # If we are in downswing
        if self._in_downswing:
            # Test if downswing continues
            if current_low < self._swing_l:
                # Treat current low as new swing low
                self._swing_l = current_low

            # Test if downswing reverses
            if current_high - self._swing_l > current_swing_filter:
                # If so, we have an upswing
                self._in_downswing = False

                # Treat current low as new swing low
                self._swing_l = current_low

                # Treat current high as new swing high
                self._swing_h = current_high

                # Append positive float to the list
                self._swing_events.append(self.UP_SWING)

                # Return dummy float
                return 0.0

            # Append falsy float as it is a continuation
            self._swing_events.append(0.0)

            # Return dummy float
            return 0.0

        # Otherwise, we are in upswing

        # Test if upswing continues
        if current_high > self._swing_h:
            # Treat current high as new swing high
            self._swing_h = current_high

        # Test if upswing reverses
        if self._swing_h - current_low > current_swing_filter:
            # If so, we have downswing
            self._in_downswing = True

            # Append negative float to the list
            self._swing_events.append(self.DOWN_SWING)

            # Return dummy float
            return 0.0

        # Append falsy float as it is a continuation
        self._swing_events.append(0.0)

        # Return dummy float
        return 0.0
