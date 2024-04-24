import numpy as np
import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL


class KeyReversalsCalculator(BaseCalculator):
    """
    Key Reversals calculator.

    Evans, Futures, 1985.
    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
    ) -> None:
        """
        Construct Key Reversals calculator.

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

        # Fill NaNs with 0
        self.dataframe["kr"].fillna(0, inplace=True)

    def __calc_kr(self, series: pd.Series, dataframe: pd.DataFrame) -> float:
        """
        Calculate rolling key reversals for a given window.

        :param series: Series which is used for indexing out rolling window.
        :param dataframe: Original dataframe acting as a source of rolling window.
        :returns: Latest calculated entry from processed window.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = dataframe.loc[series.index]

        # Get previous close, low, and high columns
        rolling_df["p_close"] = rolling_df["close"].shift(1)
        rolling_df["p_low"] = rolling_df["low"].shift(1)
        rolling_df["p_high"] = rolling_df["high"].shift(1)

        # Calculate expanding average over previous closes
        # and shift by 1 to accommodate for t-2
        rolling_df["p_close_avg"] = rolling_df["p_close"].expanding().mean().shift(1)

        # Drop NaNs to properly calculate minimum lows
        rolling_df.dropna(inplace=True)

        # Find the lowest low amongst previous lows
        rolling_df["min_low"] = np.minimum.accumulate(rolling_df["p_low"])

        # Find the highest high amongst previous highs
        rolling_df["max_high"] = np.maximum.accumulate(rolling_df["p_high"])

        # Construct and combine conditions for long key reversal
        rolling_df.loc[
            (rolling_df["p_close"] < rolling_df["p_close_avg"])
            & (rolling_df["low"] < rolling_df["min_low"])
            & (rolling_df["high"] > rolling_df["p_high"])
            & (rolling_df["close"] > rolling_df["p_close"]),
            "kr",
        ] = LONG_SIGNAL

        # Construct and combine conditions for short key reversal
        rolling_df.loc[
            (rolling_df["p_close"] > rolling_df["p_close_avg"])
            & (rolling_df["high"] > rolling_df["max_high"])
            & (rolling_df["low"] < rolling_df["p_low"])
            & (rolling_df["close"] < rolling_df["p_close"]),
            "kr",
        ] = SHORT_SIGNAL

        # Return latest entry from processed window as integer
        return rolling_df["kr"].iloc[-1]
