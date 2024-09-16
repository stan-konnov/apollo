from pandas import DataFrame

from apollo.calculations.engulfing_futures_pattern import (
    EngulfingFuturesPatternCalculator,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base.base_strategy import BaseStrategy
from apollo.strategies.base.vix_enhanced_strategy import VIXEnhancedStrategy
from apollo.strategies.base.volatility_adjusted_strategy import (
    VolatilityAdjustedStrategy,
)


class EngulfingFuturesMeanReversion(
    BaseStrategy,
    VIXEnhancedStrategy,
    VolatilityAdjustedStrategy,
):
    """
    Engulfing Futures Mean Reversion Strategy.

    This strategy takes long positions when:

    * Bearish Engulfing Pattern is detected in S&P 500 Futures,
    indicating a potential reversion after considerable price decrease.

    OR

    * VIX signal is long, indicating increasing volatility,
    forcing the price down and potentially triggering a mean reversion.

    This strategy takes short positions when:

    * Bullish Engulfing Pattern is detected in S&P 500 Futures,
    indicating a potential reversion after considerable price increase.

    OR

    * VIX signal is short, indicating decreasing volatility,
    forcing the price up and potentially triggering a mean reversion.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        doji_threshold: float,
    ) -> None:
        """
        Construct Engulfing Futures Mean Reversion Strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        :param doji_threshold: Threshold for identifying candlestick as Doji.
        """
        super().__init__(dataframe, window_size)

        BaseStrategy.__init__(self, dataframe, window_size)
        VIXEnhancedStrategy.__init__(self, dataframe, window_size)
        VolatilityAdjustedStrategy.__init__(self, dataframe, window_size)

        self._efp_calculator = EngulfingFuturesPatternCalculator(
            dataframe=dataframe,
            window_size=window_size,
            doji_threshold=doji_threshold,
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

        long = (
            (self._dataframe["spf_ep"] == self._efp_calculator.BEARISH_PATTERN)
            | (
                (self._dataframe["adj close"] < self._dataframe["prev_close"])
                & (
                    self._dataframe["spf_sp_tm1"]
                    == self._efp_calculator.BULLISH_PATTERN
                )
            )
            | (self._dataframe["spf_tp"] == self._efp_calculator.BEARISH_PATTERN)
            | (self._dataframe["spf_hp_tm1"] == self._efp_calculator.BULLISH_PATTERN)
            | (self._dataframe["vix_signal"] == LONG_SIGNAL)
        )

        self._dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = (
            (self._dataframe["spf_ep"] == self._efp_calculator.BULLISH_PATTERN)
            | (
                (self._dataframe["adj close"] > self._dataframe["prev_close"])
                & (
                    self._dataframe["spf_sp_tm1"]
                    == self._efp_calculator.BEARISH_PATTERN
                )
            )
            | (self._dataframe["spf_tp"] == self._efp_calculator.BULLISH_PATTERN)
            | (self._dataframe["spf_hp_tm1"] == self._efp_calculator.BEARISH_PATTERN)
            | (self._dataframe["vix_signal"] == SHORT_SIGNAL)
        )

        self._dataframe.loc[short, "signal"] = SHORT_SIGNAL
