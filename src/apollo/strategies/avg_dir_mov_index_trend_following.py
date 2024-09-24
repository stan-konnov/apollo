import pandas as pd

from apollo.calculations.average_directional_movement_index import (
    AverageDirectionalMovementIndexCalculator,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base.base_strategy import BaseStrategy
from apollo.strategies.base.vix_enhanced_strategy import VIXEnhancedStrategy
from apollo.strategies.base.volatility_adjusted_strategy import (
    VolatilityAdjustedStrategy,
)


class AverageDirectionalMovementIndexTrendFollowing(
    BaseStrategy,
    VIXEnhancedStrategy,
    VolatilityAdjustedStrategy,
):
    """Average Directional Movement Index Trend Following Strategy."""

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct Average Directional Movement Index Trend Following Strategy.

        TODO: I'm a mean reversion

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        """

        BaseStrategy.__init__(self, dataframe, window_size)
        VIXEnhancedStrategy.__init__(self, dataframe, window_size)
        VolatilityAdjustedStrategy.__init__(self, dataframe, window_size)

        self._adx_calculator = AverageDirectionalMovementIndexCalculator(
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

        self._adx_calculator.calculate_average_directional_movement_index()

    def _mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        long = (
            (self._dataframe["adj close"] < self._dataframe["prev_close"])
            & (self._dataframe["pdi"] > self._dataframe["prev_pdi"])
            & (self._dataframe["mdi"] > self._dataframe["prev_mdi"])
            # & (self._dataframe["adx"] > self._dataframe["prev_adx"])
            # & (self._dataframe["adxr"] > self._dataframe["prev_adxr"])
            # & (self._dataframe["pdm"] > self._dataframe["prev_pdm"])
            # & (self._dataframe["mdm"] > self._dataframe["prev_mdm"])
        )

        # & (self._dataframe["adx"] > self._dataframe["adxr"])
        # & (abs(self._dataframe["pdi"]) > abs(self._dataframe["mdi"]))

        self._dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = (
            (self._dataframe["adj close"] > self._dataframe["prev_close"])
            & (self._dataframe["pdi"] < self._dataframe["prev_pdi"])
            & (self._dataframe["mdi"] < self._dataframe["prev_mdi"])
            # & (self._dataframe["adx"] < self._dataframe["prev_adx"])
            # & (self._dataframe["adxr"] < self._dataframe["prev_adxr"])
            # & (self._dataframe["pdm"] < self._dataframe["prev_pdm"])
            # & (self._dataframe["mdm"] < self._dataframe["prev_mdm"])
        )

        # & (self._dataframe["adx"] < self._dataframe["adxr"])
        # & (abs(self._dataframe["pdi"]) < abs(self._dataframe["mdi"]))

        self._dataframe.loc[short, "signal"] = SHORT_SIGNAL
