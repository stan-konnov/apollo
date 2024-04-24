import numpy as np
import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class KeyReversalCalculator(BaseCalculator):
    """
    Key Reversal calculator.

    Evans, Futures, 1985.
    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
    ) -> None:
        """
        Construct Key Reversal calculator.

        :param dataframe: Dataframe to calculate key reversals for.
        :param window_size: Window size for rolling key reversal calculation.
        """

        super().__init__(dataframe, window_size)

    def calculate_key_reversals(self) -> None:
        """Calculate rolling key reversals."""

        self.dataframe["kr"] = (
            self.dataframe["close"]
            .rolling(self.window_size)
            .apply(
                self.__calc_kr,
                args=(self.dataframe,),
            )
        )

    def __calc_kr(self, series: pd.Series, dataframe: pd.DataFrame) -> float:
        """
        Calculate rolling key reversal for a given window.

        :param series: Series which is used for indexing out rolling window.
        :param dataframe: Original dataframe acting as a source of rolling window.
        :returns: Latest calculated entry from processed window.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = dataframe.loc[series.index]

        # From TSMKeyReversal (long), Kaufman, 2020 (AND logic):
        #
        # t = current bar
        # t-1 = previous bar
        # t-2 = bar before previous bar
        #
        # t-1 close < avg(..., t-2) close
        # t low < min(..., t-1) low
        # t high > t-1 high
        # t close > t-1 close

        # Write previous close, low, and high columns
        rolling_df["p_close"] = rolling_df["close"].shift(1)
        rolling_df["p_low"] = rolling_df["low"].shift(1)
        rolling_df["p_high"] = rolling_df["high"].shift(1)

        # Calculate expanding average over previous closes
        # and shift by 1 to accommodate for t-2
        rolling_df["p_close_avg"] = rolling_df["p_close"].expanding().mean().shift(1)

        # Drop NaNs to properly calculate minimum lows
        rolling_df.dropna(inplace=True)

        # Find the minimum low amongst previous lows
        rolling_df["min_low"] = np.minimum.accumulate(rolling_df["p_low"])

        # Construct and combine conditions for key reversal
        kr = (
            (rolling_df["p_close"] < rolling_df["p_close_avg"])
            & (rolling_df["low"] < rolling_df["min_low"])
            & (rolling_df["high"] > rolling_df["p_high"])
            & (rolling_df["close"] > rolling_df["p_close"])
        )

        # Return latest entry from processed window as integer
        return int(kr.iloc[-1])
