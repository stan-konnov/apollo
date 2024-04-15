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

        # Calculate rolling True Range
        self.dataframe["tr"] = self.dataframe["adj close"].rolling(
            self.window_size,
        ).apply(
            self.__calc_tr, args=(self.dataframe, ),
        )

        # Calculate Average True Range using J. Welles Wilder's WMA of TR
        self.dataframe["atr"] = self.dataframe["tr"].ewm(
            alpha=1 / self.window_size,
            min_periods=self.window_size,
            adjust=False,
        ).mean()


    def __calc_tr(self, series: pd.Series, dataframe: pd.DataFrame) -> None:
        """
        Calculate rolling TR for a given window.

        :param series: Series which is used for indexing out rolling window.
        :param dataframe: Original dataframe acting as a source of rolling window.
        :returns: Latest calculated entry from processed window.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = dataframe.loc[series.index]

        # Get high, low, and previous close
        high = rolling_df["high"]
        low = rolling_df["low"]
        prev_close = rolling_df["adj close"].shift()

        # Calculate True Range for each row, where TR is:
        # max(|Ht - Lt|, |Ht - Ct-1|, |Ct-1 - Lt|)
        # Kaufman, Trading Systems and Methods, 2020, p.850
        true_range = [high - low, high - prev_close, prev_close - low]

        # Bring to absolute values
        true_range = [tr.abs() for tr in true_range]

        # Get the max out of 3 operations
        true_range = pd.concat(true_range, axis=1).max(axis=1)

        # Return latest entry from processed window
        return true_range.iloc[-1]
