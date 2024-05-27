import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class MovingAverageConvergenceDivergenceCalculator(BaseCalculator):
    """
    Moving Average Convergence Divergence (MACD) calculator.

    Calculates the MACD based on the difference between
    short-term and long-term exponential moving averages.

    Calculates MACD Signal Line based on the
    exponential moving average of the MACD line.

    Donadio and Ghosh, Algorithmic Trading, 2019, 1st ed.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
        fast_ema_period: int,
        slow_ema_period: int,
    ) -> None:
        """
        Construct MACD calculator.

        :param dataframe: Dataframe to calculate APO for.
        :param window_size: Window size for rolling APO calculation.
        :param fast_ema_period: Window size for fast EMA calculation.
        :param slow_ema_period: Window size for slow EMA calculation.
        """

        super().__init__(dataframe, window_size)

        self.fast_ema_period = fast_ema_period
        self.slow_ema_period = slow_ema_period

    def calculate_moving_average_convergence_divergence(self) -> None:
        """Calculate MACD and MACD Signal Line."""

        # Calculate fast EMA
        fast_ema = (
            self.dataframe["adj close"]
            .ewm(
                alpha=1 / self.fast_ema_period,
                min_periods=self.fast_ema_period,
                adjust=False,
            )
            .mean()
        )

        # Calculate slow EMA
        slow_ema = (
            self.dataframe["adj close"]
            .ewm(
                alpha=1 / self.slow_ema_period,
                min_periods=self.slow_ema_period,
                adjust=False,
            )
            .mean()
        )

        # Calculate MACD expressed as the
        # difference between fast and slow EMAs
        self.dataframe["macd"] = fast_ema - slow_ema

        # Finally, calculate MACD Signal
        # Line as the EMA of the MACD line
        self.dataframe["macdsl"] = (
            self.dataframe["macd"]
            .ewm(
                alpha=1 / self.window_size,
                min_periods=self.window_size,
                adjust=False,
            )
            .mean()
        )
