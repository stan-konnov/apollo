import numpy as np
import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class BollingerBandsCalculator(BaseCalculator):
    """
    Bollinger Bands Calculator.

    Calculates the Bollinger Bands expressed
    as +/- N standard deviations from the simple moving average.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    Donadio and Ghosh, Algorithmic Trading, 2019, 1st ed.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
        channel_sd_spread: float,
    ) -> None:
        """
        Construct Bollinger Bands calculator.

        :param dataframe: Dataframe to calculate Bollinger Bands for.
        :param window_size: Window size for rolling Bollinger Bands calculation.
        :param channel_sd_spread: Standard deviation spread for channel bounds.
        """

        super().__init__(dataframe, window_size)

        self.channel_sd_spread = channel_sd_spread

        self.lb_band: list[float] = []
        self.ub_band: list[float] = []

    def calculate_bollinger_bands(self) -> None:
        """Calculate Bollinger Bands."""

        # Fill bands arrays with N NaN, where N = window size
        self.lb_band = np.full((1, self.window_size - 1), np.nan).flatten().tolist()
        self.ub_band = np.full((1, self.window_size - 1), np.nan).flatten().tolist()

        # Calculate simple moving average to act as the middle band
        self.dataframe["sma"] = (
            self.dataframe["adj close"]
            .rolling(
                self.window_size,
            )
            .mean()
        )

        # Calculate bands by using SMA and standard deviation
        self.dataframe["adj close"].rolling(self.window_size).apply(
            self._calc_bands,
            args=(self.dataframe,),
        )

        # Drop SMA from the dataframe
        self.dataframe.drop(columns="sma", inplace=True)

    def _calc_bands(self, series: pd.Series, dataframe: pd.DataFrame) -> float:
        """
        Calculate rolling Bollinger Bands.

        :param series: Series which is used for indexing out rolling window.
        :param dataframe: Original dataframe acting as a source of rolling window.
        :returns: Dummy float to satisfy Pandas' return value.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = dataframe.loc[series.index]

        # Calculate standard deviation of adjusted close
        std = series.std()

        # Calculate lower and upper bands
        l_band = rolling_df["sma"] - std * self.channel_sd_spread
        u_band = rolling_df["sma"] + std * self.channel_sd_spread

        self.lb_band.append(l_band[-1])
        self.ub_band.append(u_band[-1])

        # Return dummy float
        return 0.0
