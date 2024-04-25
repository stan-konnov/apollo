from pandas import DataFrame

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.distribution_moments import DistributionMomentsCalculator
from apollo.calculations.linear_regression_channel import (
    LinearRegressionChannelCalculator,
)
from apollo.calculations.swing_events import SwingEventsCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy


class CustomCombination(BaseStrategy):
    """
    Custom Combination.

    This strategy combines all the strategies in the OR fashion to apply
    multiple approaches (be it mean reversion or trend following, or momentum) at once.

    For detailed logic on position taking, refer to the individual strategies involved:

    * Swing Events Mean Reversion
    * Linear Regression Channel Mean Reversion
    * Skewness Kurtosis Volatility Trend Following
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        swing_filter: float,
        channel_sd_spread: float,
        kurtosis_threshold: float,
        volatility_multiplier: float,
    ) -> None:
        """
        Construct Custom Combination Strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        :param swing_filter: Swing filter for determining swing highs and lows.
        :param channel_sd_spread: Spread of standard deviation for channel.
        :param kurtosis_threshold: Threshold to define when kurtosis is peaking.
        :param volatility_multiplier: Multiplier to apply against average volatility.
        """

        self._validate_parameters(
            [
                ("swing_filter", swing_filter, float),
                ("channel_sd_spread", channel_sd_spread, float),
                ("kurtosis_threshold", kurtosis_threshold, float),
                ("volatility_multiplier", volatility_multiplier, float),
            ],
        )

        super().__init__(dataframe, window_size)

        self.kurtosis_threshold = kurtosis_threshold
        self.volatility_multiplier = volatility_multiplier

        self.se_calculator = SwingEventsCalculator(
            dataframe=dataframe,
            window_size=window_size,
            swing_filter=swing_filter,
        )

        self.lrc_calculator = LinearRegressionChannelCalculator(
            dataframe=dataframe,
            window_size=window_size,
            channel_sd_spread=channel_sd_spread,
        )

        self.at_calculator = AverageTrueRangeCalculator(dataframe, window_size)
        self.dm_calculator = DistributionMomentsCalculator(dataframe, window_size)

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self.__calculate_indicators()
        self.__mark_trading_signals()
        self.dataframe.dropna(inplace=True)

    def __calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self.se_calculator.calculate_swing_events()
        self.at_calculator.calculate_average_true_range()
        self.dm_calculator.calculate_distribution_moments()
        self.lrc_calculator.calculate_linear_regression_channel()

    def __mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        long = (
            (self.dataframe["se"] == self.se_calculator.DOWN_SWING)
            | (
                (self.dataframe["adj close"] <= self.dataframe["l_bound"])
                & (self.dataframe["slope"] <= self.dataframe["prev_slope"])
            )
            | (
                (self.dataframe["skew"] < 0)
                & (self.dataframe["kurt"] < self.kurtosis_threshold)
                & (
                    self.dataframe["tr"]
                    > self.dataframe["atr"] * self.volatility_multiplier
                )
            )
        )
        self.dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = (
            (self.dataframe["se"] == self.se_calculator.UP_SWING)
            | (self.dataframe["adj close"] >= self.dataframe["u_bound"])
            & (self.dataframe["slope"] >= self.dataframe["prev_slope"])
            | (
                (self.dataframe["skew"] > 0)
                & (self.dataframe["kurt"] < self.kurtosis_threshold)
                & (
                    self.dataframe["tr"]
                    > self.dataframe["atr"] * self.volatility_multiplier
                )
            )
        )
        self.dataframe.loc[short, "signal"] = SHORT_SIGNAL
