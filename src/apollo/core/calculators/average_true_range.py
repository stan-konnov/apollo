import pandas as pd

from apollo.core.calculators.base_calculator import BaseCalculator


class AverageTrueRangeCalculator(BaseCalculator):
    """
    Average True Range (ATR) Calculator.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    Wilder, New Concepts in Technical Trading Systems, 1978.
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct ATR Calculator.

        :param dataframe: Dataframe to calculate ATR for.
        :param window_size: Window size for rolling ATR calculation.
        """

        super().__init__(dataframe, window_size)

    def calculate_average_true_range(self) -> None:
        """Calculate rolling ATR via rolling TR and EMA."""

        # Calculate rolling True Range
        self._dataframe["tr"] = (
            self._dataframe["adj close"].rolling(self._window_size).apply(self._calc_tr)
        )

        # Calculate Average True Range using J. Welles Wilder's WMA of TR
        self._dataframe["atr"] = (
            self._dataframe["tr"]
            .ewm(
                alpha=1 / self._window_size,
                min_periods=self._window_size,
                adjust=False,
            )
            .mean()
        )

    def _calc_tr(self, series: pd.Series) -> float:
        """
        Calculate rolling TR for a given window.

        :param series: Series which is used for indexing out rolling window.
        :returns: Latest calculated entry from processed window.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[series.index]

        # Get high, low, and previous close
        high = rolling_df.iloc[-1]["adj high"]
        low = rolling_df.iloc[-1]["adj low"]
        prev_close = rolling_df.iloc[-1]["prev_close"]

        # Calculate True Range for each row, where TR is:
        # max(|Ht - Lt|, |Ht - Ct-1|, |Ct-1 - Lt|)
        # Kaufman, Trading Systems and Methods, 2020, p.850
        true_range = [high - low, high - prev_close, prev_close - low]

        # Bring to maximum absolute value and return
        return max([abs(tr) for tr in true_range])
