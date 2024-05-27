from pandas import DataFrame

from apollo.calculations.moving_average_convergence_divergence import (
    MovingAverageConvergenceDivergenceCalculator,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy


class MovingAverageConvergenceDivergenceMeanReversion(BaseStrategy):
    """
    Work in progress.

    Donadio and Ghosh, Algorithmic Trading, 2019, 1st ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        fast_ema_period: float,
        slow_ema_period: float,
    ) -> None:
        """Work in progress."""

        self._validate_parameters(
            [
                ("fast_ema_period", fast_ema_period, float),
                ("slow_ema_period", slow_ema_period, float),
            ],
        )

        super().__init__(dataframe, window_size)

        # NOTE: We cast fast and slow EMA periods to integers
        # as they are used as window sizes in the calculations.
        # Yet, the strategy consumes them as floats since parameter
        # optimizer is designed to create combinations of float values.
        self.macd_calculator = MovingAverageConvergenceDivergenceCalculator(
            dataframe=dataframe,
            window_size=window_size,
            fast_ema_period=int(fast_ema_period),
            slow_ema_period=int(slow_ema_period),
        )

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self.__calculate_indicators()
        self.__mark_trading_signals()
        self.dataframe.dropna(inplace=True)

    def __calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self.macd_calculator.calculate_moving_average_convergence_divergence()

    def __mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        self.dataframe.loc[
            self.dataframe["macd"] < self.dataframe["macdsl"],
            "signal",
        ] = LONG_SIGNAL

        self.dataframe.loc[
            self.dataframe["macd"] > self.dataframe["macdsl"],
            "signal",
        ] = SHORT_SIGNAL
