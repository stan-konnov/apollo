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

        fast_std = (
            self.dataframe["adj close"]
            .rolling(
                window=self.fast_ema_period,
            )
            .std()
        )

        fast_ema = (
            self.dataframe["adj close"]
            .rolling(window=self.fast_ema_period)
            .apply(
                self._calc_vol_adj_ema,
                args=(self.fast_ema_period, fast_std),
            )
        )

        slow_std = (
            self.dataframe["adj close"]
            .rolling(
                window=self.slow_ema_period,
            )
            .std()
        )

        slow_ema = (
            self.dataframe["adj close"]
            .rolling(window=self.slow_ema_period)
            .apply(
                self._calc_vol_adj_ema,
                args=(self.slow_ema_period, slow_std),
            )
        )

        # Calculate APO
        self.dataframe["apo"] = fast_ema - slow_ema

    def _calc_vol_adj_ema(
        self,
        series: pd.Series,
        ema_window_size: int,
        standard_deviation: pd.Series,
    ) -> float:
        """Calculate volatility adjusted fast EMA."""

        # Calculate average standard deviation for the window
        average_standard_deviation = standard_deviation.mean()

        # Calculate standard deviation factor for the window
        standard_deviation_factor = (standard_deviation / average_standard_deviation)[
            -1
        ]

        # Calculate volatility adjusted smoothing factor
        alpha = 1 / ema_window_size * standard_deviation_factor

        # Calculate volatility adjusted EMA
        vol_adjusted_ema = series.ewm(alpha=alpha, adjust=False).mean()

        return vol_adjusted_ema[-1]
