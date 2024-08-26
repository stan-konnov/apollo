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
    """

    # A constant to represent up trend
    UP_TREND: float = 1.0

    # A constant to represent down trend
    DOWN_TREND: float = -1.0

    # A constant to represent current trend
    CURRENT_TREND: float = 0.0

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """Construct Dunnigan Futures Trend Calculator."""

        super().__init__(dataframe, window_size)

    def calculate_dunnigan_futures_trend(self) -> None:
        """Calculate Dunnigan Futures Trend."""

        self._dataframe["dtf"] = (
            self._dataframe["adj close"]
            .rolling(window=self._window_size)
            .apply(self._calc_dtf)
        )

    def _calc_dtf(self, series: pd.Series) -> float:
        """
        Calculate rolling Dunnigan's Futures Trend.

        :param series: Series which is used for indexing out rolling window.
        :returns: Latest calculated entry from processed window.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[series.index]

        # Initialize falsy values for uptrend and downtrend
        up_trend = False
        down_trend = False

        # Get the highest high and lowest low (NOTE: OUTSIDE OF THE WINDOW)
        hh: float = rolling_df["spf high"].max()
        ll: float = rolling_df["spf low"].min()

        # Get current high and low prices
        curr_h: float = rolling_df.iloc[-1]["spf high"]
        curr_l: float = rolling_df.iloc[-1]["spf low"]

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
        # is greater than or equal to the highest high
        if up_trend and curr_h >= hh:
            # Then the trend is
            # confirmed as uptrend
            return self.UP_TREND

        # If we are in the downtrend and current low
        # is less than or equal to the lowest low
        if down_trend and curr_l <= ll:
            # Then the trend is
            # confirmed as downtrend
            return self.DOWN_TREND

        return 0.0
