import numpy as np
import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class KeltnerChannelCalculator(BaseCalculator):
    """
    Keltner Channel Calculator.

    Keltner Channel is a volatility-based indicator that
    consists of bands around moving average of the price
    and are calculated based off ATR and supplied multiplier.

    NOTE: this calculator uses McNicholl Moving Average
    in order to make the channel more responsive
    to the volatility of the instrument.

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
        Construct Keltner Channel calculator.

        :param dataframe: Dataframe to calculate Keltner Channel for.
        :param window_size: Window size for rolling Keltner Channel calculation.
        :param volatility_multiplier: ATR multiplier for channel bounds.
        """

        super().__init__(dataframe, window_size)

        self.volatility_multiplier = volatility_multiplier

        self.lkc_bound: list[float] = []
        self.ukc_bound: list[float] = []

    def calculate_keltner_channel(self) -> None:
        """Calculate Keltner Channel."""

        # Fill bounds arrays with N NaN, where N = window size
        self.lkc_bound = np.full((1, self.window_size - 1), np.nan).flatten().tolist()
        self.ukc_bound = np.full((1, self.window_size - 1), np.nan).flatten().tolist()

        # Calculate bounds by using SMA and ATR
        self.dataframe["adj close"].rolling(self.window_size).apply(
            self._calc_chan,
            args=(self.dataframe,),
        )

        # Preserve bounds on the dataframe
        self.dataframe["lkc_bound"] = self.lkc_bound
        self.dataframe["ukc_bound"] = self.ukc_bound

    def _calc_chan(self, series: pd.Series, dataframe: pd.DataFrame) -> float:
        """
        Calculate rolling Keltner Channel.

        :param series: Series which is used for indexing out rolling window.
        :param dataframe: Original dataframe acting as a source of rolling window.
        :returns: Dummy float to satisfy Pandas' return value.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = dataframe.loc[series.index]

        # Calculate lower and upper channel bounds
        # expressed as +/- ATR * multiplier from the moving average
        lkc_bound = rolling_df["mnma"] - rolling_df["atr"] * self.volatility_multiplier
        ukc_bound = rolling_df["mnma"] + rolling_df["atr"] * self.volatility_multiplier

        self.lkc_bound.append(lkc_bound[-1])
        self.ukc_bound.append(ukc_bound[-1])

        # Return dummy float
        return 0.0
