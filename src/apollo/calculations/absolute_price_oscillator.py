import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class AbsolutePriceOscillatorCalculator(BaseCalculator):
    """
    Absolute Price Oscillator (APO) calculator.

    Calculates the APO based on the difference between
    short-term and long-term exponential moving averages.
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
        Construct APO calculator.

        :param dataframe: Dataframe to calculate APO for.
        :param window_size: Window size for rolling APO calculation.
        :param fast_ema_period: Window size for fast EMA calculation.
        :param slow_ema_period: Window size for slow EMA calculation.
        """

        super().__init__(dataframe, window_size)

        self.fast_ema_period = fast_ema_period
        self.slow_ema_period = slow_ema_period

    def calculate_absolute_price_oscillator(self) -> None:
        """
        Calculate Absolute Price Oscillator (APO).

        By taking the difference between short-term and long-term EMAs.
        """

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

        # Calculate APO
        self.dataframe["apo"] = fast_ema - slow_ema
