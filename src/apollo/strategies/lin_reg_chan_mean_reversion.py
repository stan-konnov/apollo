from pandas import DataFrame

from apollo.calculations.linear_regression_channel import (
    LinearRegressionChannelCalculator,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base.base_strategy import BaseStrategy
from apollo.strategies.base.vix_reinforced_strategy import VIXEnhancedStrategy
from apollo.strategies.base.volatility_adjusted_strategy import (
    VolatilityAdjustedStrategy,
)


class LinearRegressionChannelMeanReversion(
    BaseStrategy,
    VIXEnhancedStrategy,
    VolatilityAdjustedStrategy,
):
    """
    Linear Regression Channel Mean Reversion.

    This strategy takes long positions when:

    * Adjusted close crosses below lower bound of the channel,
    indicating that instrument entered oversold zone.

    * Slope of the channel is decreasing,
    indicating continuation of movement down and away from the mean.

    This strategy takes short positions when:

    * Adjusted close crosses above upper bound of the channel,
    indicating that instrument entered overbought zone.

    * Slope of the channel is increasing,
    indicating continuation of movement up and away from the mean.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        channel_sd_spread: float,
    ) -> None:
        """
        Construct Linear Regression Channel Strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        :param channel_sd_spread: Standard deviation spread for channel bounds.
        """

        self._validate_parameters(
            [
                ("channel_sd_spread", channel_sd_spread, float),
            ],
        )

        BaseStrategy.__init__(self, dataframe, window_size)
        VIXEnhancedStrategy.__init__(self, dataframe, window_size)
        VolatilityAdjustedStrategy.__init__(self, dataframe, window_size)

        self._lrc_calculator = LinearRegressionChannelCalculator(
            dataframe=dataframe,
            window_size=window_size,
            channel_sd_spread=channel_sd_spread,
        )

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self._calculate_indicators()
        self._mark_trading_signals()
        self._dataframe.dropna(inplace=True)

    def _calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self._lrc_calculator.calculate_linear_regression_channel()

    def _mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        long = (self._dataframe["adj close"] <= self._dataframe["l_bound"]) & (
            self._dataframe["slope"] <= self._dataframe["prev_slope"]
        ) | (self._dataframe["vix_signal"] == LONG_SIGNAL)

        self._dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = (self._dataframe["adj close"] >= self._dataframe["u_bound"]) & (
            self._dataframe["slope"] >= self._dataframe["prev_slope"]
        ) | (self._dataframe["vix_signal"] == SHORT_SIGNAL)

        self._dataframe.loc[short, "signal"] = SHORT_SIGNAL
