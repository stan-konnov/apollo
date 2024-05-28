from pandas import DataFrame

from apollo.calculations.momentum.absolute_price_oscillator import (
    AbsolutePriceOscillatorCalculator,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy


class AbsolutePriceOscillatorMeanReversion(BaseStrategy):
    """
    Work in progress.

    TODO: perhaps, use average APO within window as oscillator threshold.

    Donadio and Ghosh, Algorithmic Trading, 2019, 1st ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        fast_ema_period: float,
        slow_ema_period: float,
        oscillator_threshold: float,
    ) -> None:
        """Work in progress."""

        self._validate_parameters(
            [
                ("fast_ema_period", fast_ema_period, float),
                ("slow_ema_period", slow_ema_period, float),
                ("oscillator_threshold", oscillator_threshold, float),
            ],
        )

        super().__init__(dataframe, window_size)

        self.oscillator_threshold = oscillator_threshold

        # NOTE: We cast fast and slow EMA periods to integers
        # as they are used as window sizes in the calculations.
        # Yet, the strategy consumes them as floats since parameter
        # optimizer is designed to create combinations of float values.
        self.apo_calculator = AbsolutePriceOscillatorCalculator(
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

        self.apo_calculator.calculate_absolute_price_oscillator()

    def __mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        self.dataframe.loc[
            self.dataframe["apo"] < self.oscillator_threshold * -1,
            "signal",
        ] = LONG_SIGNAL

        self.dataframe.loc[
            self.dataframe["apo"] > self.oscillator_threshold,
            "signal",
        ] = SHORT_SIGNAL
