import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from apollo.calculations.base_calculator import BaseCalculator

"""
Please use DEMA instead of McNicholl Moving Average.
"""


class McNichollMovingAverageCalculator(BaseCalculator):
    """
    McNicholl Moving Average Calculator.

    McNicholl Moving Average is a variation of the Exponential Moving Average
    that uses a smoothing factor to calculate the weighted average of the data.

    Is an extension of the Double Exponential Moving Average (DEMA), therefore,
    the smoothing factor is calculated by dividing 2 by the window size plus 1,
    instead of regular Wilders smoothing factor of 1 / window size.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """Construct McNicholl Moving Average calculator."""

        super().__init__(dataframe, window_size)

    def calculate_mcnicholl_moving_average(self) -> None:
        """Calculate McNicholl Moving Average."""

        # Calculate initial SMA
        ema_1 = (
            self.dataframe["adj close"]
            .ewm(
                alpha=1 / self.window_size,
                min_periods=self.window_size,
                adjust=False,
            )
            .mean()
        )

        ema_2 = ema_1.ewm(
            alpha=1 / self.window_size,
            min_periods=self.window_size,
            adjust=False,
        ).mean()

        dema = 2 * ema_1 - ema_2

        self.dataframe["mnma"] = dema

    def _calc_trix(self, series: pd.Series) -> float:
        """Calculate Triple Exponential Smoothing."""

        model = ExponentialSmoothing(series)

        fit = model.fit()

        # Get the fitted values and forecasts
        triple_exp_smoothing_values = fit.fittedvalues

        return triple_exp_smoothing_values.iloc[-1]
