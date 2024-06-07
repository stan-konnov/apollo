import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from apollo.calculations.base_calculator import BaseCalculator

# It's work in progress
# ruff: noqa

"""
Please use HMA instead of McNicholl Moving Average.

Simple Moving Average (SMA): The SMA is the average of a set of prices over a specified
time period, with equal weight given to each price.
It's easy to calculate but can lag behind recent price movements.

Exponential Moving Average (EMA): The EMA gives more weight to recent prices,
making it more responsive to recent price changes compared to the SMA.
It's calculated by giving more weight to the most recent data points.

Weighted Moving Average (WMA): The WMA assigns weights to each data point,
with more weight given to recent data points.
It's similar to the EMA but allows for more customization of the weight distribution.

Triangular Moving Average (TMA): The TMA is a smoothed version of the SMA, where the
data points are averaged using a triangular weighting scheme.
It gives more weight to data points closer to the center of the time period.

Variable Moving Average (VMA): The VMA adjusts its sensitivity based on market
conditions, similar to the KAMA. It can be more responsive during periods of
high volatility and less responsive during periods of low volatility.

Hull Moving Average (HMA): The HMA attempts to address the issue of lagging behind
price movements by using the square root of the time period for smoothing.
It's designed to be more responsive while maintaining smoothness.

Volume Weighted Moving Average (VWMA): The VWMA gives more weight to data points with
higher trading volume, reflecting the importance of volume in price movements.

Arithmetic Moving Average (AMA): The AMA adjusts the smoothing factor dynamically
based on market conditions, aiming to reduce lag during trending markets
while smoothing out noise during ranging markets.

Adaptive Moving Average (Adaptive MA): Similar to the AMA, the Adaptive MA adjusts its
sensitivity based on market conditions,
aiming to adapt to changes in volatility and trend.
"""


class HullMovingAverageCalculator(BaseCalculator):
    """
    Work in progress.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """Construct Hull Moving Average calculator."""

        super().__init__(dataframe, window_size)

    def calculate_hull_moving_average(self) -> None:
        """Calculate Hull Moving Average."""

        # DEMA!
        # Calculate initial SMA
        # ema_1 = (
        #     self.dataframe["adj close"]
        #     .ewm(
        #         alpha=1 / self.window_size,
        #         min_periods=self.window_size,
        #         adjust=False,
        #     )
        #     .mean()
        # )

        # ema_2 = ema_1.ewm(
        #     alpha=1 / self.window_size,
        #     min_periods=self.window_size,
        #     adjust=False,
        # ).mean()

        # dema = 2 * ema_1 - ema_2

        # HMA!
        def wma(data: pd.Series, window: int) -> pd.Series:
            weights = np.arange(1, window + 1)

            wma_values = data.rolling(window=window).apply(
                lambda x: np.sum(x * weights) / np.sum(weights), raw=True
            )

            return wma_values

        half_window = self.window_size // 2

        # Step 1: Calculate WMA of data and half-window
        wma_data = wma(self.dataframe["adj close"], self.window_size)
        wma_half = wma(self.dataframe["adj close"], half_window)

        # Step 2: Calculate difference
        diff = 2 * wma_half - wma_data

        # Step 3: Calculate WMA of the difference with square root of window
        sqrt_window = int(np.sqrt(self.window_size))
        hma = wma(diff, sqrt_window)

        self.dataframe["hma"] = hma
