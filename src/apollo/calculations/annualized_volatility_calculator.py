import numpy as np
import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class AnnualizedVolatilityCalculator(BaseCalculator):
    """Annualized Volatility Calculator."""

    # Constant to
    # represent number of
    # trading days in a year
    N_TRADING_DAYS = 252

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct Annualized Volatility Calculator.

        :param dataframe: Dataframe to calculate annualized volatility for.
        :param window_size: Window size for rolling annualized volatility calculation.
        """

        super().__init__(dataframe, window_size)

    def calculate_annualized_volatility(self) -> None:
        """Calculate Annualized Volatility."""

        # Calculate log returns
        log_returns = self._dataframe["adj close"].pct_change()

        # Calculate rolling standard deviation
        rolling_std = log_returns.rolling(
            self._window_size,
        ).std()

        # Calculate annualized rolling volatility
        self._dataframe["arv"] = rolling_std * np.sqrt(self.N_TRADING_DAYS)
