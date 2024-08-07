import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class ConnersVixReversalCalculator(BaseCalculator):
    """Conners' VIX Reversal Calculator class."""

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
