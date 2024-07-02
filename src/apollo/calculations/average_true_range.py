import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class AverageTrueRangeCalculator(BaseCalculator):
    """
    Average True Range (ATR) calculator.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    Wilder, New Concepts in Technical Trading Systems, 1978.
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct ATR calculator.

        :param dataframe: Dataframe to calculate ATR for.
        :param window_size: Window size for rolling ATR calculation.
        """

        super().__init__(dataframe, window_size)

    def calculate_average_true_range(self) -> None:
        """Calculate rolling ATR via rolling TR and EMA."""

        # Precalculate previous close
        self.dataframe["prev_close"] = self.dataframe["close"].shift(1)

        # Calculate rolling True Range
        self.dataframe["tr"] = (
            self.dataframe["close"]
            .rolling(
                self.window_size,
            )
            .apply(
                self.__calc_tr,
            )
        )

        # Calculate Average True Range using J. Welles Wilder's WMA of TR
        self.dataframe["atr"] = (
            self.dataframe["tr"]
            .ewm(
                alpha=1 / self.window_size,
                min_periods=self.window_size,
                adjust=False,
            )
            .mean()
        )

        # Drop previous close as we no longer need it
        self.dataframe.drop(columns=["prev_close"], inplace=True)

    def __calc_tr(self, series: pd.Series) -> float:
        """
        Calculate rolling TR for a given window.

        :param series: Series which is used for indexing out rolling window.
        :returns: Latest calculated entry from processed window.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = self.dataframe.loc[series.index]

        # Get high, low, and previous close
        high = rolling_df["high"][-1]
        low = rolling_df["low"][-1]
        prev_close = rolling_df["prev_close"][-1]

        # Calculate True Range for each row, where TR is:
        # max(|Ht - Lt|, |Ht - Ct-1|, |Ct-1 - Lt|)
        # Kaufman, Trading Systems and Methods, 2020, p.850
        true_range = [high - low, high - prev_close, prev_close - low]

        # Bring to maximum absolute value and return
        return max([abs(tr) for tr in true_range])
