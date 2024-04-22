from pandas import DataFrame

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.distribution_moments import DistributionMomentsCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base import BaseStrategy


class SkewnessKurtosisVolatilityTrendFollowing(BaseStrategy):
    """
    Skewness Kurtosis Volatility Trend Following.

    This strategy takes long positions when:

    * Moving skewness is negative -- more prices fall above the mean than below,
    indicating positive trend.

    * Moving kurtosis is negative -- prices experiencing flatness,
    indicating orderly moves within the positive trend.

    * Volatility is above average -- price point fluctuates significantly from the rest,
    acting as reinforcement of the move within positive trend.

    This strategy takes short positions when:

    * Moving skewness is positive -- more prices fall below the mean than above,
    indicating negative trend.

    * Moving kurtosis is negative -- prices experiencing flatness,
    indicating orderly moves within the negative trend.

    * Volatility is above average -- price point fluctuates significantly from the rest,
    acting as reinforcement of the move within negative trend.

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

        super().__init__(dataframe, window_size)

        self.kurtosis_threshold = kurtosis_threshold
        self.volatility_multiplier = volatility_multiplier

        self.at_calculator = AverageTrueRangeCalculator(dataframe, window_size)
        self.dm_calculator = DistributionMomentsCalculator(dataframe, window_size)


    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self.__calculate_indicators()
        self.__mark_trading_signals()
        self.dataframe.dropna(inplace=True)


    def __calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self.at_calculator.calculate_average_true_range()
        self.dm_calculator.calculate_distribution_moments()


    def __mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        long = (
            (self.dataframe["skew"] < 0) &
            (self.dataframe["kurt"] < self.kurtosis_threshold) &
            (self.dataframe["tr"] > self.dataframe["atr"] * self.volatility_multiplier)
        )
        self.dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = (
            (self.dataframe["skew"] > 0) &
            (self.dataframe["kurt"] < self.kurtosis_threshold) &
            (self.dataframe["tr"] > self.dataframe["atr"] * self.volatility_multiplier)
        )
        self.dataframe.loc[short, "signal"] = SHORT_SIGNAL
