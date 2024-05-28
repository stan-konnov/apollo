import numpy as np
import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class SupportResistanceTouchCountCalculator(BaseCalculator):
    """
    Support Resistance Touch Count calculator.

    Calculates rolling support and resistance levels
    touch counts based on the threshold of tolerance.
    Donadio and Ghosh, Algorithmic Trading, 2019, 1st ed.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
        tolerance_threshold: float,
    ) -> None:
        """
        Construct Support Resistance Touch Count calculator.

        :param dataframe: Dataframe to calculate touch counts for.
        :param window_size: Window size for rolling touch counts calculation.
        :param tolerance_threshold: Tolerance threshold for support-resistance levels.
        """

        super().__init__(dataframe, window_size)

        self.tolerance_threshold = tolerance_threshold

        # Initialize touch counters
        self.sup_touched: int = 0
        self.res_touched: int = 0

        # Initialize touch count arrays
        self.sup_touch_count: list[int] = []
        self.res_touch_count: list[int] = []

    def calculate_support_resistance_touch_count(self) -> None:
        """Calculate rolling support resistance touch counts."""

        # Fill support and resistance touch counts
        # arrays with N NaN, where N = window size
        self.sup_touch_count = (
            np.full((1, self.window_size - 1), np.nan).flatten().tolist()
        )

        self.res_touch_count = (
            np.full((1, self.window_size - 1), np.nan).flatten().tolist()
        )

        # Calculate rolling support resistance touch counts
        self.dataframe["adj close"].rolling(self.window_size).apply(
            self._calc_sr,
        )

        # Write touch counts to the dataframe
        self.dataframe["stc"] = self.sup_touch_count
        self.dataframe["rtc"] = self.res_touch_count

    def _calc_sr(self, series: pd.Series) -> float:
        """
        Calculate rolling support resistance touch counts for a given window.

        :param series: Series which is used for indexing out rolling window.
        :param dataframe: Original dataframe acting as a source of rolling window.
        :returns: Dummy float to satisfy Pandas' return value.
        """

        # Consider lowest and highest prices
        # as our support and resistance levels
        sup_level = series.min()
        res_level = series.max()

        # Calculate tolerance thresholds based on the min and max
        sup_tolerance = sup_level + self.tolerance_threshold * sup_level
        res_tolerance = res_level - self.tolerance_threshold * res_level

        # Grab the current adjusted close price
        current_price = series.iloc[-1]

        # Increment the support touch counter
        # if price is within the tolerance of support
        if current_price <= sup_tolerance and current_price >= sup_level:
            self.sup_touched += 1

        # Increment the resistance touch counter
        # if price is within the tolerance of resistance
        elif current_price >= res_tolerance and current_price <= res_level:
            self.res_touched += 1

        # Reset touch counters
        # if price is outside of tolerance
        else:
            self.res_touched = 0
            self.sup_touched = 0

        # Append touch counts to arrays
        self.sup_touch_count.append(self.sup_touched)
        self.res_touch_count.append(self.res_touched)

        # Return dummy float to satisfy Pandas' return value
        return 0.0
