from pandas import DataFrame

from apollo.calculations.engulfing_futures_pattern import (
    EngulfingFuturesPatternCalculator,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base.base_strategy import BaseStrategy
from apollo.strategies.base.volatility_adjusted_strategy import (
    VolatilityAdjustedStrategy,
)


class EngulfingFuturesMeanReversion(
    BaseStrategy,
    VolatilityAdjustedStrategy,
):
    """
    Engulfing Futures Mean Reversion Strategy.

    WIP.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
    ) -> None:
        """
        Construct Engulfing Futures Mean Reversion Strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        """
        super().__init__(dataframe, window_size)

        BaseStrategy.__init__(self, dataframe, window_size)
        VolatilityAdjustedStrategy.__init__(self, dataframe, window_size)

        self._efp_calculator = EngulfingFuturesPatternCalculator(
            dataframe=dataframe,
            window_size=window_size,
        )

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self._calculate_indicators()
        self._mark_trading_signals()
        self._dataframe.dropna(inplace=True)

    def _calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self._efp_calculator.calculate_engulfing_futures_pattern()

    def _mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        self._dataframe.loc[
            self._dataframe["spfep"] == self._efp_calculator.BEARISH_ENGULFING,
            "signal",
        ] = LONG_SIGNAL

        self._dataframe.loc[
            self._dataframe["spfep"] == self._efp_calculator.BULLISH_ENGULFING,
            "signal",
        ] = SHORT_SIGNAL
