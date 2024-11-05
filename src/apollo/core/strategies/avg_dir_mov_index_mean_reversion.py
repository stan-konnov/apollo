import pandas as pd

from apollo.core.calculators.average_directional_movement_index import (
    AverageDirectionalMovementIndexCalculator,
)
from apollo.core.strategies.base.base_strategy import BaseStrategy
from apollo.core.strategies.base.vix_enhanced_strategy import VIXEnhancedStrategy
from apollo.core.strategies.base.volatility_adjusted_strategy import (
    VolatilityAdjustedStrategy,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL


class AverageDirectionalMovementIndexMeanReversion(
    BaseStrategy,
    VIXEnhancedStrategy,
    VolatilityAdjustedStrategy,
):
    """
    Average Directional Movement Index Mean Reversion Strategy.

    This strategy takes long positions when:

    * Adjusted close is below the previous close,
    indicating that the price is decreasing.

    * True Directional Movement is below the previous value,
    indicating that the instrument is within a negative trend.

    * Amplitude of True Directional Movement against it's average
    is below the previous value, indicating flattening of
    the negative trend and potential mean reversion.

    OR

    * Adjusted close is below the previous close,
    indicating that the price is decreasing.

    * Plus Directional Indicator is above the previous value,
    indicating that the positive trend is strengthening.

    * Minus Directional Indicator is above the previous value,
    indicating that the negative trend is weakening.

    OR

    * VIX signal is long, indicating increasing volatility,
    forcing the price down and potentially triggering a mean reversion.

    This strategy takes short positions when:

    * Adjusted close is above the previous close,
    indicating that the price is increasing.

    * True Directional Movement is above the previous value,
    indicating that the instrument is within a positive trend.

    * Amplitude of True Directional Movement against it's average
    is above the previous value, indicating sharpening of
    the positive trend and potential mean reversion.

    OR

    * Adjusted close is above the previous close,
    indicating that the price is increasing.

    * Plus Directional Indicator is below the previous value,
    indicating that the positive trend is weakening.

    * Minus Directional Indicator is below the previous value,
    indicating that the negative trend is strengthening.

    OR

    * VIX signal is short, indicating decreasing volatility,
    forcing the price up and potentially triggering a mean reversion.


    NOTE: This logic is adapted from:

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    Colby, The Encyclopedia of Technical Market Indicators, 2003, 2nd ed.
    Wilder, "Selection and Direction", Technical Analysis in Commodities, 1980.

    And does not follow the original implementation to-the-letter.
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct Average Directional Movement Index Mean Reversion Strategy.

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
            & (self._dataframe["dx"] < self._dataframe["prev_dx"])
            & (self._dataframe["dx_adx_ampl"] < self._dataframe["prev_dx_adx_ampl"])
            | (
                (self._dataframe["adj close"] < self._dataframe["prev_close"])
                & (self._dataframe["pdi"] > self._dataframe["prev_pdi"])
                & (self._dataframe["mdi"] > self._dataframe["prev_mdi"])
            )
        ) | (self._dataframe["vix_signal"] == LONG_SIGNAL)

        self._dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = (
            (self._dataframe["adj close"] > self._dataframe["prev_close"])
            & (self._dataframe["dx"] > self._dataframe["prev_dx"])
            & (self._dataframe["dx_adx_ampl"] > self._dataframe["prev_dx_adx_ampl"])
            | (
                (self._dataframe["adj close"] > self._dataframe["prev_close"])
                & (self._dataframe["pdi"] < self._dataframe["prev_pdi"])
                & (self._dataframe["mdi"] < self._dataframe["prev_mdi"])
            )
        ) | (self._dataframe["vix_signal"] == SHORT_SIGNAL)

        self._dataframe.loc[short, "signal"] = SHORT_SIGNAL
