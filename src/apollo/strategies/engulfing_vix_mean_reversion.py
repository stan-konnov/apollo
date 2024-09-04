from pandas import DataFrame

from apollo.calculations.engulfing_vix_pattern import (
    EngulfingVIXPatternCalculator,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base.base_strategy import BaseStrategy
from apollo.strategies.base.volatility_adjusted_strategy import (
    VolatilityAdjustedStrategy,
)


class EngulfingVIXMeanReversion(
    BaseStrategy,
    VolatilityAdjustedStrategy,
):
    """
    VIX Expansion Contraction Mean Reversion Strategy.

    WIP DOCS.

    This strategy takes long positions when:

    * Current VIX open is lower than the previous VIX open.

    * Current VIX close is higher than the previous VIX close.

    * Current VIX close is higher than the current VIX open.

    Combination of these factors point to an upside
    range expansion in implied volatility and a sharp decline
    in the underlying asset price with the potential for a reversal.

    This strategy takes short positions when:

    * Current VIX open is higher than the previous VIX open.

    * Current VIX close is lower than the previous VIX close.

    * Current VIX close is lower than the current VIX open.

    Combination of these factors point to a downside
    range contraction in implied volatility and a steady rise
    in the underlying asset price with the potential for a reversal.

    "This capitalizes on the concept that non-professional traders liquidate
    when volatility increases, and buy when volatility decreases,
    commonly termed 'risk on' and 'risk off'".

    Kaufman, Trading Systems and Methods, 2020, 6th ed., p 863.

    The strategy, therefore, aims to reverse this logic
    and capture the reversal points in the underlying asset price.

    NOTE: This strategy proved to be effective as an enhancement
    strategy and is also used in conjunction with other strategies.
    The logic applied here can also be found in VIX Enhanced Strategy.

    NOTE: This is an adapted version of Conners' VIX Reversals
    and does not follow the original logic to the letter.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
    ) -> None:
        """
        Construct Engulfing VIX Mean Reversion Strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        """

        BaseStrategy.__init__(self, dataframe, window_size)
        VolatilityAdjustedStrategy.__init__(self, dataframe, window_size)

        self._evp_calculator = EngulfingVIXPatternCalculator(
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

        self._evp_calculator.calculate_engulfing_vix_pattern()

    def _mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        self._dataframe.loc[
            self._dataframe["vixep"] == self._evp_calculator.BULLISH_ENGULFING,
            "signal",
        ] = LONG_SIGNAL

        self._dataframe.loc[
            self._dataframe["vixep"] == self._evp_calculator.BEARISH_ENGULFING,
            "signal",
        ] = SHORT_SIGNAL
