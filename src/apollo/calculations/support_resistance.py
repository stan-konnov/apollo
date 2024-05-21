import numpy as np
import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class SupportResistanceCalculator(BaseCalculator):
    """
    Support and Resistance calculator.

    Calculates rolling support and resistance
    levels based on threshold of tolerance.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
        sup_tolerance: float,
        res_tolerance: float,
    ) -> None:
        """
        Construct Support and Resistance calculator.

        :param dataframe: Dataframe to calculate support and resistance levels for.
        :param window_size: Window size for rolling support and resistance calculation.
        :param sup_tolerance: Tolerance for support level calculation.
        :param res_tolerance: Tolerance for resistance level calculation.
        """

        super().__init__(dataframe, window_size)

        self.sup_tolerance = sup_tolerance
        self.res_tolerance = res_tolerance

        self.sup_touch_count: list[float] = []
        self.res_touch_count: list[float] = []

    def calculate_support_resistance(self) -> None:
        """Calculate rolling support and resistance levels."""

        # Fill support and resistance touch counts
        # arrays with N NaN, where N = window size
        self.sup_touch_count = (
            np.full((1, self.window_size - 1), np.nan).flatten().tolist()
        )

        self.res_touch_count = (
            np.full((1, self.window_size - 1), np.nan).flatten().tolist()
        )

        # Calculate rolling support and resistance touch counts
        self.dataframe["adj close"].rolling(self.window_size).apply(
            self._calc_sr,
            args=(self.dataframe,),
        )

    def _calc_sr(self, series: pd.Series, dataframe: pd.DataFrame) -> float:
        """
        Calculate rolling support and resistance touch counts for a given window.

        :param series: Series which is used for indexing out rolling window.
        :param dataframe: Original dataframe acting as a source of rolling window.
        :returns: Dummy float to satisfy Pandas' return value.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = dataframe.loc[series.index]

        # Consider lowest and highest prices
        # as our support and resistance levels
        sup_level = rolling_df["adj close"].min()
        res_level = rolling_df["adj close"].max()

        # Calculate the range between them
        sup_res_range = res_level - sup_level

        # Calculate tolerance thresholds
        sup_tolerance = sup_level + self.sup_tolerance * sup_res_range
        res_tolerance = res_level - self.res_tolerance * sup_res_range

        return 0.0
