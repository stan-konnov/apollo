import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class VixFutureConvergenceDivergenceCalculator(BaseCalculator):
    """
    VIX Futures Convergence Divergence Calculator.

    Calculates percentage change difference between VIX and S&P 500 Futures.
    Captures increasing/decreasing convergence and divergence between the two.
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Initialize the VIX Futures Convergence Divergence Calculator.

        :param dataframe: Dataframe to calculate Convergence Divergence for.
        :param window_size: Size of the window for Convergence Divergence calculation.

        NOTE: even though we accept window_size parameter,
        calculator does not perform any rolling calculations.
        """
        super().__init__(dataframe, window_size)

    def calculate_vix_futures_convergence_divergence(self) -> None:
        """Calculate VIX Futures Convergence Divergence."""

        # Get previous close price
        # Is a necessary for strategies revolving
        # around VIX and S&P 500 Futures percentage change
        self._dataframe["prev_close"] = self._dataframe["adj close"].shift(1)

        # Calculate percentage change for VIX and S&P 500 Futures
        self._dataframe["vix_pct_change"] = self._dataframe["vix close"].pct_change()
        self._dataframe["spf_pct_change"] = self._dataframe["spf close"].pct_change()

        # Calculate percentage change difference between VIX and S&P 500 Futures
        self._dataframe["vix_spf_pct_diff"] = (
            self._dataframe["vix_pct_change"] - self._dataframe["spf_pct_change"]
        )

        # Shift to get previous percentage change difference
        self._dataframe["prev_vix_spf_pct_diff"] = self._dataframe[
            "vix_spf_pct_diff"
        ].shift(1)
