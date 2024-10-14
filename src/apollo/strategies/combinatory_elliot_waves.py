from pandas import DataFrame

from apollo.calculations.elliot_waves import ElliotWavesCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base.base_strategy import BaseStrategy
from apollo.strategies.base.volatility_adjusted_strategy import (
    VolatilityAdjustedStrategy,
)


class CombinatoryElliotWaves(
    BaseStrategy,
    VolatilityAdjustedStrategy,
):
    """
    Combinatory Elliot Waves Strategy.

    WIP.

    1. Reoptimize again.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        fast_oscillator_period: float,
        slow_oscillator_period: float,
    ) -> None:
        """
        Construct Combinatory Elliot Waves Strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        :param fast_oscillator_period: Fast period for Elliot Waves Oscillator.
        :param slow_oscillator_period: Slow period for Elliot Waves Oscillator.
        """

        self._validate_parameters(
            [
                ("fast_oscillator_period", fast_oscillator_period, float),
                ("slow_oscillator_period", slow_oscillator_period, float),
            ],
        )

        BaseStrategy.__init__(self, dataframe, window_size)
        VolatilityAdjustedStrategy.__init__(self, dataframe, window_size)

        self._ew_calculator = ElliotWavesCalculator(
            dataframe=dataframe,
            window_size=window_size,
            fast_oscillator_period=fast_oscillator_period,
            slow_oscillator_period=slow_oscillator_period,
        )

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self._calculate_indicators()
        self._mark_trading_signals()
        self._dataframe.dropna(inplace=True)

    def _calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self._ew_calculator.calculate_elliot_waves()

    def _mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        self._dataframe.loc[
            self._dataframe["ew"] == self._ew_calculator.UPWARD_WAVE,
            "signal",
        ] = LONG_SIGNAL

        self._dataframe.loc[
            self._dataframe["ew"] == self._ew_calculator.DOWNWARD_WAVE,
            "signal",
        ] = SHORT_SIGNAL
