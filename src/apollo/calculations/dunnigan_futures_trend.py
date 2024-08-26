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

    # A constant to represent long-term trend
    LONG_TERM_TREND: float = 1.0

    # A constant to represent short-term trend
    SHORT_TERM_TREND: float = -1.0

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

        # Get last three futures high prices
        high_at_t_minus_two, high_at_t_minus_one, high_at_t = list(
            rolling_df.iloc[self._window_size - 3 :]["spf high"],
        )

        # Get last three futures low prices
        low_at_t_minus_two, low_at_t_minus_one, low_at_t = list(
            rolling_df.iloc[self._window_size - 3 :]["spf low"],
        )

        # Determine if we are in uptrend
        # or downtrend based on making higher highs
        # and higher lows or lower highs and lower lows
        if (
            high_at_t > high_at_t_minus_one
            and high_at_t > high_at_t_minus_two
            and low_at_t > low_at_t_minus_one
            and low_at_t > low_at_t_minus_two
        ):
            up_trend = True
            down_trend = False

        elif (
            high_at_t < high_at_t_minus_one
            and high_at_t < high_at_t_minus_two
            and low_at_t < low_at_t_minus_one
            and low_at_t < low_at_t_minus_two
        ):
            up_trend = False
            down_trend = True

        print(up_trend, down_trend)  # noqa: T201

        return 0.0
