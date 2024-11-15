import numpy as np
import pandas as pd

from apollo.calculators.base_calculator import BaseCalculator


class KeltnerChannelCalculator(BaseCalculator):
    """
    Keltner Channel Calculator.

    Keltner Channel is a volatility-based indicator that
    consists of bands around moving average of the price
    and are calculated based off ATR and supplied multiplier.

    NOTE: this calculator uses Hull Moving Average
    in order to make the channel more responsive
    to short-term price movements.

    NOTE: since all of our strategies are volatility-based,
    this calculator implicitly has access to calculated ATR values.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
        volatility_multiplier: float,
    ) -> None:
        """
        Construct Keltner Channel Calculator.

        :param dataframe: Dataframe to calculate Keltner Channel for.
        :param window_size: Window size for rolling Keltner Channel calculation.
        :param volatility_multiplier: ATR multiplier for channel bounds.
        """

        super().__init__(dataframe, window_size)

        self._volatility_multiplier = volatility_multiplier

        self._lkc_bound: list[float] = []
        self._ukc_bound: list[float] = []

    def calculate_keltner_channel(self) -> None:
        """Calculate Keltner Channel."""

        # Fill bounds arrays with N NaN, where N = window size
        self._lkc_bound = np.full((1, self._window_size - 1), np.nan).flatten().tolist()
        self._ukc_bound = np.full((1, self._window_size - 1), np.nan).flatten().tolist()

        # Calculate bounds by using SMA and ATR
        self._dataframe["adj close"].rolling(self._window_size).apply(self._calc_chan)

        # Preserve bounds on the dataframe
        self._dataframe["lkc_bound"] = self._lkc_bound
        self._dataframe["ukc_bound"] = self._ukc_bound

    def _calc_chan(self, series: pd.Series) -> float:
        """
        Calculate rolling Keltner Channel.

        :param series: Series which is used for indexing out rolling window.
        :returns: Dummy float to satisfy Pandas' return value.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[series.index]

        # Calculate lower and upper channel bounds
        # expressed as +/- ATR * multiplier from the moving average
        lkc_bound = rolling_df["hma"] - rolling_df["atr"] * self._volatility_multiplier
        ukc_bound = rolling_df["hma"] + rolling_df["atr"] * self._volatility_multiplier

        self._lkc_bound.append(lkc_bound.iloc[-1])
        self._ukc_bound.append(ukc_bound.iloc[-1])

        # Return dummy float
        return 0.0
