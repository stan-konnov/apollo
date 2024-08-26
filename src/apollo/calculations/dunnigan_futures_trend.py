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

    CT = trend high or low

    currhigh/low = start with inf -inf

    !!!Appending up, down or no trend should be last!!!

    Rewrite the logic from TSM to the letter, more work in this needed

    VARIABLES TO DEFINE OUTSIDE THE WINDOW:

    trend(0 | 1 | -1),
    downtrend(false),
    uptrend(false),
    curlow(np.inf),
    curhigh(-np.inf),
    CTlow(0),
    CThigh(0),
    """

    # A constant to represent no trend
    NO_TREND: float = 0.0

    # A constant to represent up trend
    UP_TREND: float = 1.0

    # A constant to represent down trend
    DOWN_TREND: float = -1.0

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """Construct Dunnigan Futures Trend Calculator."""

        self._trend_l = 0.0
        self._trend_h = 0.0

        self._futures_trend: list[float] = []

        super().__init__(dataframe, window_size)

    def calculate_dunnigan_futures_trend(self) -> None:
        """Calculate Dunnigan Futures Trend."""

        # Record the low of the first bar (before rolling window) as trend low
        self._trend_l = self._dataframe.iloc[self._window_size - 2]["spf low"]

        # Record the high of the first bar (before rolling window) as trend high
        self._trend_h = self._dataframe.iloc[self._window_size - 2]["spf high"]

        # Fill trend array with N NaN, where N = window size
        self._futures_trend = (
            np.full((1, self._window_size - 1), np.nan).flatten().tolist()
        )

        # Calculate rolling Dunnigan's Futures Trend
        self._dataframe["adj close"].rolling(window=self._window_size).apply(
            self._calc_dft,
        )

        # Write futures trend to the dataframe
        self._dataframe["dft"] = self._futures_trend

    def _calc_dft(self, series: pd.Series) -> float:
        """
        Calculate rolling Dunnigan's Futures Trend.

        :param series: Series which is used for indexing out rolling window.
        :returns: Dummy float to satisfy Pandas' return value.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[series.index]

        # Initialize falsy values for uptrend and downtrend
        # NOTE: THIS SHOULD MOVE OUTSIDE THE WINDOW!
        up_trend = False
        down_trend = False

        # Grab the value of the previous trend
        prev_trend = self._futures_trend[-1]

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
            h_at_t > h_at_t_minus_one
            and h_at_t > h_at_t_minus_two
            and l_at_t > l_at_t_minus_one
            and l_at_t > l_at_t_minus_two
        ):
            up_trend = True
            down_trend = False

        # We are in the downtrend if the current high
        # is lower than the previous two highs
        # and the current low is lower
        # than the previous two lows
        elif (
            h_at_t < h_at_t_minus_one
            and h_at_t < h_at_t_minus_two
            and l_at_t < l_at_t_minus_one
            and l_at_t < l_at_t_minus_two
        ):
            up_trend = False
            down_trend = True

        # If we are in the uptrend and current high
        # is greater than or equal to the trend high
        if up_trend and h_at_t >= self._trend_h:
            # Then the trend is
            # confirmed as uptrend

            # DO NOT APPEND HERE,
            # BUT DEFINE current trend OUTSIDE AND ASSIGN
            self._futures_trend.append(self.UP_TREND)

            # If previous trend was downtrend
            # then recompute the trend high
            if prev_trend == self.DOWN_TREND:
                self._trend_h = h_at_t

            # Otherwise,
            # recompute the trend low
            else:
                self._trend_l = l_at_t

            # Return dummy float
            return 0.0

        # If we are in the uptrend and current
        # high is lower than the trend high
        if up_trend and h_at_t < self._trend_h:
            # Then, recompute the trend high
            self._trend_h = h_at_t

        # If we are in the downtrend and current low
        # is less than or equal to the trend low
        if down_trend and l_at_t <= self._trend_l:
            # Then the trend is
            # confirmed as downtrend

            # DO NOT APPEND HERE,
            # BUT DEFINE current trend OUTSIDE AND ASSIGN
            self._futures_trend.append(self.DOWN_TREND)

            # If previous trend was uptrend
            # then recompute the trend low
            if prev_trend == self.UP_TREND:
                self._trend_l = l_at_t

            # Otherwise,
            # recompute the trend high
            else:
                self._trend_h = h_at_t

            # Return dummy float
            return 0.0

        # If we are in the downtrend and current
        # low is greater than the trend low
        if down_trend and l_at_t > self._trend_l:
            # Then, recompute the trend low
            self._trend_l = l_at_t

        # No trend with confirmation = no trend detected
        self._futures_trend.append(self.NO_TREND)

        # Return dummy float
        return 0.0
