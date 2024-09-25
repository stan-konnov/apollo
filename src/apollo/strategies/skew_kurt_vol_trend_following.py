from pandas import DataFrame

from apollo.calculations.distribution_moments import DistributionMomentsCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base.base_strategy import BaseStrategy
from apollo.strategies.base.vix_enhanced_strategy import VIXEnhancedStrategy
from apollo.strategies.base.volatility_adjusted_strategy import (
    VolatilityAdjustedStrategy,
)


class SkewnessKurtosisVolatilityTrendFollowing(
    BaseStrategy,
    VIXEnhancedStrategy,
    VolatilityAdjustedStrategy,
):
    """
    Skewness Kurtosis Volatility Trend Following.

    This strategy takes long positions when:

    * Moving skewness is negative -- more prices fall above the mean than below,
    indicating positive trend.

    * Moving kurtosis is negative -- prices experiencing flatness,
    indicating orderly moves within the positive trend.

    * Volatility is above average -- price point fluctuates significantly from the rest,
    acting as reinforcement of the move within positive trend.

    OR

    * VIX signal is long, indicating increasing volatility,
    forcing the price down and potentially triggering a mean reversion.

    This strategy takes short positions when:

    * Moving skewness is positive -- more prices fall below the mean than above,
    indicating negative trend.

    * Moving kurtosis is negative -- prices experiencing flatness,
    indicating orderly moves within the negative trend.

    * Volatility is above average -- price point fluctuates significantly from the rest,
    acting as reinforcement of the move within negative trend.

    OR

    * VIX signal is short, indicating decreasing volatility,
    forcing the price up and potentially triggering a mean reversion.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        kurtosis_threshold: float,
        volatility_multiplier: float,
    ) -> None:
        """
        Construct Skewness Kurtosis Volatility Strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        :param kurtosis_threshold: Threshold to define when kurtosis is peaking.
        :param volatility_multiplier: Multiplier to apply against average volatility.
        """

        self._validate_parameters(
            [
                ("kurtosis_threshold", kurtosis_threshold, float),
                ("volatility_multiplier", volatility_multiplier, float),
            ],
        )

        BaseStrategy.__init__(self, dataframe, window_size)
        VIXEnhancedStrategy.__init__(self, dataframe, window_size)
        VolatilityAdjustedStrategy.__init__(self, dataframe, window_size)

        self._kurtosis_threshold = kurtosis_threshold
        self._volatility_multiplier = volatility_multiplier

        self._dm_calculator = DistributionMomentsCalculator(dataframe, window_size)

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self._calculate_indicators()
        self._mark_trading_signals()

        self._dataframe.dropna(inplace=True)

    def _calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self._dm_calculator.calculate_distribution_moments()

    def _mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        long = (
            (self._dataframe["skew"] < 0)
            & (self._dataframe["kurt"] < self._kurtosis_threshold)
            & (
                self._dataframe["tr"]
                > self._dataframe["atr"] * self._volatility_multiplier
            )
        ) | (self._dataframe["vix_signal"] == LONG_SIGNAL)

        self._dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = (
            (self._dataframe["skew"] > 0)
            & (self._dataframe["kurt"] < self._kurtosis_threshold)
            & (
                self._dataframe["tr"]
                > self._dataframe["atr"] * self._volatility_multiplier
            )
        ) | (self._dataframe["vix_signal"] == SHORT_SIGNAL)

        self._dataframe.loc[short, "signal"] = SHORT_SIGNAL
