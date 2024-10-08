from pandas import DataFrame

from apollo.calculations.elliot_waves_calculator import ElliotWavesCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base.base_strategy import BaseStrategy
from apollo.strategies.base.volatility_adjusted_strategy import (
    VolatilityAdjustedStrategy,
)


class ElliotWavesMeanReversion(
    BaseStrategy,
    VolatilityAdjustedStrategy,
):
    """
    Elliot Waves Mean Reversion.

    WIP.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        fast_oscillator_period: int,
        slow_oscillator_period: int,
    ) -> None:
        """
        Construct Linear Regression Channel Strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        :param fast_oscillator_period: Fast period for Elliot Waves Oscillator.
        :param slow_oscillator_period: Slow period for Elliot Waves Oscillator.
        """

        self._validate_parameters(
            [
                ("fast_oscillator_period", fast_oscillator_period, int),
                ("slow_oscillator_period", slow_oscillator_period, int),
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

        long = (self._dataframe["ewo"] < 0) & (
            (self._dataframe["ew"] == self._ew_calculator.ELLIOT_WAVE_2)
            | (self._dataframe["ew"] == self._ew_calculator.ELLIOT_WAVE_4)
        )

        self._dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = (self._dataframe["ewo"] > 0) & (
            (self._dataframe["ew"] == self._ew_calculator.ELLIOT_WAVE_1)
            | (self._dataframe["ew"] == self._ew_calculator.ELLIOT_WAVE_3)
        )

        self._dataframe.loc[short, "signal"] = SHORT_SIGNAL
