from pandas import DataFrame

from apollo.core.calculations.swing_events import SwingEventsCalculator
from apollo.core.strategies.base.base_strategy import BaseStrategy
from apollo.core.strategies.base.volatility_adjusted_strategy import (
    VolatilityAdjustedStrategy,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL


class SwingEventsMeanReversion(
    BaseStrategy,
    VolatilityAdjustedStrategy,
):
    """
    Swing Events Mean Reversion.

    This strategy takes long positions when:

    * Downward swing event is detected, indicating that instrument is in downswing.

    This strategy takes short positions when:

    * Upward swing event is detected, indicating that instrument is in upswing.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        swing_filter: float,
    ) -> None:
        """
        Construct Swing Events Mean Reversion Strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        :param swing_filter: Swing filter for determining swing highs and lows.
        """

        self._validate_parameters(
            [
                ("swing_filter", swing_filter, float),
            ],
        )

        BaseStrategy.__init__(self, dataframe, window_size)
        VolatilityAdjustedStrategy.__init__(self, dataframe, window_size)

        self._se_calculator = SwingEventsCalculator(
            dataframe=dataframe,
            window_size=window_size,
            swing_filter=swing_filter,
        )

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self._calculate_indicators()
        self._mark_trading_signals()
        self._dataframe.dropna(inplace=True)

    def _calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self._se_calculator.calculate_swing_events()

    def _mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        self._dataframe.loc[
            self._dataframe["se"] == self._se_calculator.DOWN_SWING,
            "signal",
        ] = LONG_SIGNAL

        self._dataframe.loc[
            self._dataframe["se"] == self._se_calculator.UP_SWING,
            "signal",
        ] = SHORT_SIGNAL
