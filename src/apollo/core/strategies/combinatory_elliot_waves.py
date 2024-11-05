from pandas import DataFrame

from apollo.core.calculators.elliot_waves import ElliotWavesCalculator
from apollo.core.strategies.base.base_strategy import BaseStrategy
from apollo.core.strategies.base.volatility_adjusted_strategy import (
    VolatilityAdjustedStrategy,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL


class CombinatoryElliotWaves(
    BaseStrategy,
    VolatilityAdjustedStrategy,
):
    """
    Combinatory Elliot Waves Strategy.

    This strategy takes long positions when:

    * One of the upward Elliot Waves is detected.
    Namely, waves 1, 3, or 5 within the uptrend, or wave 2 within the downtrend.

    This strategy takes short positions when:

    * One of the downward Elliot Waves is detected.
    Namely, waves 2 or 4 within the uptrend, or waves 1 and 3 within the downtrend.

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
