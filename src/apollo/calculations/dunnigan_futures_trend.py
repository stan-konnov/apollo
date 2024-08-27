import numpy as np
import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class DunniganFuturesTrendCalculator(BaseCalculator):
    """
    Dunnigan Futures Trend Calculator.

    Is based on the Ruggiero's adaptation of Dunnigan's trend system,
    that revolves around identifying higher highs / higher lows and
    lower highs / lower lows to determine the trend of a security.

    Is applied to futures prices to produce enhancing trading signals.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    Dunnigan, Selected Studies in Speculation, 1954.
    Ruggiero, "Dunnigan's Way", Futures, 1998.

    NOTE: there is a difference between Current Trend High and Low
    and curr high and low (check TSM source again)
    """

    # A constant to represent up trend
    UP_TREND: float = 1.0

    # A constant to represent down trend
    DOWN_TREND: float = -1.0

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """Construct Dunnigan Futures Trend Calculator."""

        self._curr_l = np.inf
        self._curr_h = -np.inf

        self._counter_trend_l = 0.0
        self._counter_trend_h = 0.0

        self._up_trend = False
        self._down_trend = False
        self._current_trend = 0.0

        self._trend_line: list[float] = []

        super().__init__(dataframe, window_size)

    def calculate_dunnigan_futures_trend(self) -> None:
        """Calculate Dunnigan Futures Trend."""

        # Record the low of the first bar (before rolling window) as trend low
        self._trend_l = self._dataframe.iloc[self._window_size - 2]["spf low"]

        # Record the high of the first bar (before rolling window) as trend high
        self._trend_h = self._dataframe.iloc[self._window_size - 2]["spf high"]

        # Fill trend array with N NaN, where N = window size
        self._trend_line = (
            np.full((1, self._window_size - 1), np.nan).flatten().tolist()
        )

        # Calculate rolling Dunnigan's Futures Trend
        self._dataframe["adj close"].rolling(window=self._window_size).apply(
            self._calc_dft,
        )

        # Write futures trend to the dataframe
        self._dataframe["dft"] = self._trend_line

    def _calc_dft(self, series: pd.Series) -> float:  # noqa: C901
        """
        Calculate rolling Dunnigan's Futures Trend.

        :param series: Series which is used for indexing out rolling window.
        :returns: Dummy float to satisfy Pandas' return value.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[series.index]

        # Grab the value of the previous trend
        prev_trend = self._trend_line[-1]

        # Get last three futures high prices
        h_at_t_minus_two, h_at_t_minus_one, h_at_t = list(
            rolling_df.iloc[self._window_size - 3 :]["spf high"],
        )

        # Get last three futures low prices
        l_at_t_minus_two, l_at_t_minus_one, l_at_t = list(
            rolling_df.iloc[self._window_size - 3 :]["spf low"],
        )

        # We are in the uptrend if the current high
        # is greater than the previous two highs
        # and the current low is greater
        # than the previous two lows
        if (
            h_at_t > h_at_t_minus_one > h_at_t_minus_two
            and l_at_t > l_at_t_minus_one > l_at_t_minus_two
        ):
            self._up_trend = True
            self._down_trend = False

        # We are in the downtrend if the current high
        # is lower than the previous two highs
        # and the current low is lower
        # than the previous two lows
        elif (
            h_at_t < h_at_t_minus_one < h_at_t_minus_two
            and l_at_t < l_at_t_minus_one < l_at_t_minus_two
        ):
            self._up_trend = False
            self._down_trend = True

        # If we are in the uptrend and current high
        # is greater than or equal to the trend high
        if self._up_trend and h_at_t >= self._curr_h:
            # Then the trend is
            # confirmed as uptrend
            self._current_trend = self.UP_TREND

        # If we are in the downtrend and current low
        # is less than or equal to the trend low
        if self._down_trend and l_at_t <= self._curr_l:
            # Then the trend is
            # confirmed as downtrend
            self._current_trend = self.DOWN_TREND

        # Record the current counter
        # trend low in a short-term uptrend
        if (
            self._current_trend == self.UP_TREND
            and h_at_t > self._curr_h
            and h_at_t > h_at_t_minus_one
        ):
            self._counter_trend_l = l_at_t

        # Record the current counter
        # trend high in a short-term downtrend
        if (
            self._current_trend == self.DOWN_TREND
            and l_at_t < self._curr_l
            and l_at_t < l_at_t_minus_one
        ):
            self._counter_trend_h = h_at_t

        # Reset current high in the direction
        # of the current trend when the trend changes
        if self._current_trend == self.UP_TREND and prev_trend == self.DOWN_TREND:
            self._curr_h = h_at_t

        # Reset current low in the direction
        # of the current trend when the trend changes
        if self._current_trend == self.DOWN_TREND and prev_trend == self.UP_TREND:
            self._curr_l = l_at_t

        # Record the current high of the current trend
        if self._current_trend == self.UP_TREND:
            if self._curr_h < h_at_t:
                self._curr_h = h_at_t

            self._curr_h = min(self._curr_h, h_at_t)

        # Record the current low of the current trend
        if self._current_trend == self.DOWN_TREND:
            if self._curr_l > l_at_t:
                self._curr_l = l_at_t

            self._curr_l = max(self._curr_l, l_at_t)

        # Append the current trend to the trend line
        self._trend_line.append(self._current_trend)

        # Return dummy float
        return 0.0
