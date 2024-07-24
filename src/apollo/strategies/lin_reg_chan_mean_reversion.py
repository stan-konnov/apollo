from pandas import DataFrame

from apollo.calculations.linear_regression_channel import (
    LinearRegressionChannelCalculator,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy


class LinearRegressionChannelMeanReversion(BaseStrategy):
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

        super().__init__(dataframe, window_size)

        self.lrc_calculator = LinearRegressionChannelCalculator(
            dataframe=dataframe,
            window_size=window_size,
            channel_sd_spread=channel_sd_spread,
        )

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self._calculate_indicators()
        self._mark_trading_signals()
        self.dataframe.dropna(inplace=True)

    def _calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self.lrc_calculator.calculate_linear_regression_channel()

    def _mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        long = (self.dataframe["adj close"] <= self.dataframe["l_bound"]) & (
            self.dataframe["slope"] <= self.dataframe["prev_slope"]
        )
        self.dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = (self.dataframe["adj close"] >= self.dataframe["u_bound"]) & (
            self.dataframe["slope"] >= self.dataframe["prev_slope"]
        )
        self.dataframe.loc[short, "signal"] = SHORT_SIGNAL
