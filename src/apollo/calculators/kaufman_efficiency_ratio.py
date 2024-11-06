import pandas as pd

from apollo.calculators.base_calculator import BaseCalculator


class KaufmanEfficiencyRatioCalculator(BaseCalculator):
    """
    Kaufman Efficiency Ratio Calculator.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct KER Calculator.

        :param dataframe: Dataframe to calculate KER for.
        :param window_size: Window size for rolling KER calculation.
        """

        super().__init__(dataframe, window_size)

    def calculate_kaufman_efficiency_ratio(self) -> None:
        """Calculate rolling Kaufman Efficiency Ratio."""

        # Shift adjusted close observations by one window size
        close_one_window_back = self._dataframe["adj close"].shift(
            self._window_size,
        )

        # Calculate absolute price difference
        # between current and previous window observations
        abs_price_differ = (self._dataframe["adj close"] - close_one_window_back).abs()

        # Calculate absolute price change
        abs_price_change = self._dataframe["adj close"].diff().abs()

        # Sum absolute price changes over the window
        abs_price_change_sum = abs_price_change.rolling(
            window=self._window_size,
            min_periods=self._window_size,
        ).sum()

        # Calculate Kaufman Efficiency Ratio
        self._dataframe["ker"] = abs_price_differ / abs_price_change_sum
