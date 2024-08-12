import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator

# ruff: noqa

"""
TODO: worst-case scenario pack VIX into
separate strategy

Original logic:

# Calculate VIX reversal to the upside
if (
    curr_high > highest_high
    and curr_close < curr_open
    and prev_close > prev_open
    and curr_range > largest_range
):
    return self.UPSIDE_REVERSAL

# Calculate VIX reversal to the downside
if (
    curr_high < highest_high
    and curr_close > curr_open
    and prev_close < prev_open
    and curr_range < largest_range
):
    return self.DOWNSIDE_REVERSAL

return self.NO_REVERSAL

https://www.whselfinvest.com/en-lu/trading-platform/free-trading-strategies/tradingsystem/40-vix-reversal

https://howtotrade.com/trading-strategies/vix/

Chart VIX and ticker prices together to investigate potential opportunities.

Ideas:

1. Use VIX slope (via OLS)?

What works so far:

# Calculate VIX reversal to the upside
if curr_open < prev_open and curr_close > prev_close:
    return self.UPSIDE_REVERSAL

# Calculate VIX reversal to the downside
if curr_open > prev_open and curr_close < prev_close:
    return self.DOWNSIDE_REVERSAL

Exposure Time [%]                   58.778915
Return (Ann.) [%]                   26.890418
Sharpe Ratio                         2.172139
Avg. Trade [%]                       0.275405
"""


class ConnersVixReversalCalculator(BaseCalculator):
    """Conners' VIX Reversal Calculator class."""

    # Constant to represent
    # reversal to the upside
    UPSIDE_REVERSAL: float = 1.0

    # Constant to represent
    # reversal to the downside
    DOWNSIDE_REVERSAL: float = -1.0

    # Constant to represent
    # no reversal to either side
    NO_REVERSAL: float = 0.0

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct Conners' VIX Reversal Calculator.

        :param dataframe: Dataframe to calculate VIX reversals for.
        :param window_size: Window size for VIX reversals calculation.
        """

        super().__init__(dataframe, window_size)

    def calculate_vix_reversals(self) -> None:
        """Calculate Conners' VIX Reversals."""

        # Precalculate VIX previous open and close
        self._dataframe["vix_prev_open"] = self._dataframe["vix open"].shift(1)
        self._dataframe["vix_prev_close"] = self._dataframe["vix close"].shift(1)

        # Precalculate VIX range
        self._dataframe["vix_range"] = abs(
            self._dataframe["vix high"] - self._dataframe["vix low"],
        )

        self._dataframe["prev_vix_range"] = self._dataframe["vix_range"].shift(1)

        # Calculate VIX reversals and write to the dataframe
        self._dataframe["cvr"] = (
            self._dataframe["vix close"]
            .rolling(self._window_size)
            .apply(self._calc_cvr)
        )

        # Drop precalculated columns as we no longer need them
        self._dataframe.drop(
            columns=["vix_prev_open", "vix_prev_close", "vix_range"],
            inplace=True,
        )

    def _calc_cvr(self, series: pd.Series) -> float:
        """
        Calculate rolling VIX Reversal for a given window.

        :param series: Series which is used for indexing out rolling window.
        :returns: Latest calculated entry from processed window.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[series.index]

        # Get the VIX highest high within the window
        highest_high = rolling_df["vix high"].max()

        # Get the largest VIX range within the window
        largest_range = rolling_df["vix_range"].max()

        # Get current VIX open, high, low, and close
        curr_open = rolling_df["vix open"].iloc[-1]
        curr_high = rolling_df["vix high"].iloc[-1]
        curr_low = rolling_df["vix low"].iloc[-1]
        curr_close = rolling_df["vix close"].iloc[-1]

        # Get previous VIX open and close
        prev_open = rolling_df["vix_prev_open"].iloc[-1]
        prev_close = rolling_df["vix_prev_close"].iloc[-1]

        # Grab current and previous VIX range
        curr_range = rolling_df["vix_range"].iloc[-1]
        prev_range = rolling_df["vix_prev_range"].iloc[-1]

        # Calculate VIX reversal to the upside
        if curr_open < prev_open and curr_close > prev_close:
            return self.UPSIDE_REVERSAL

        # Calculate VIX reversal to the downside
        if curr_open > prev_open and curr_close < prev_close:
            return self.DOWNSIDE_REVERSAL

        return self.NO_REVERSAL
