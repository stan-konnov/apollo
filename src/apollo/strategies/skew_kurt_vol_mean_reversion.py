from pandas import DataFrame

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.distribution_moments import DistributionMomentsCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base import BaseStrategy


class SkewnessKurtosisVolatilityMeanReversion(BaseStrategy):
    """
    Skewness Kurtosis Volatility Mean Reversion.

    This strategy takes long positions when:

    * Moving kurtosis is positive -- prices experiencing peakedness,
    indicating strengthening of the trend.

    * Moving skewness is negative -- more prices fall above the mean than below,
    indicating positive trend.

    * Volatility is above average -- prices are experiencing large fluctuations,
    acting as reinforcement of the move up.

    This strategy takes short positions when:

    * Moving kurtosis is negative -- prices experiencing flatness,
    indicating weakening of the trend.

    * Moving skewness is positive -- more prices fall below the mean than above,
    indicating negative trend.

    * Volatility is above average -- prices are experiencing large fluctuations,
    acting as reinforcement of the move down.

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
            (self.dataframe["kurt"] > self.kurtosis_threshold) &
            (self.dataframe["skew"] < 0) &
            (self.dataframe["tr"] > self.dataframe["atr"] * self.volatility_multiplier)
        )
        self.dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = (
            (self.dataframe["kurt"] < self.kurtosis_threshold) &
            (self.dataframe["skew"] > 0) &
            (self.dataframe["tr"] > self.dataframe["atr"] * self.volatility_multiplier)
        )
        self.dataframe.loc[short, "signal"] = SHORT_SIGNAL
