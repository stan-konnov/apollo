from pandas import DataFrame

from apollo.calculations.chaikin_accumulation_distribution import (
    ChaikinAccumulationDistributionCalculator,
)
from apollo.calculations.hull_moving_average import (
    HullMovingAverageCalculator,
)
from apollo.calculations.keltner_channel import KeltnerChannelCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy


class KeltnerChaikinTrendFollowing(BaseStrategy):
    """
    Keltner Chaikin Trend Following.

    NOTE: this strategy uses Hull Moving Average as input for
    calculation of the Keltner Channel to make the channel
    more responsive to short-term price movements.

    This strategy takes long positions when:

    * Adjusted close is above the lower Keltner Channel bound,
    indicating that instrument is within the expected volatility range.

    * Accumulation Distribution Line is increasing,
    indicating that instrument is being accumulated.

    This strategy takes short positions when:

    * Adjusted close is below the upper Keltner Channel bound,
    indicating that instrument is within the expected volatility range.

    * Accumulation Distribution Line is decreasing,
    indicating that instrument is being distributed.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        volatility_multiplier: float,
    ) -> None:
        """
        Construct Keltner Chaikin Trend Following Strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        :param volatility_multiplier: ATR multiplier for Keltner Channel.
        """

        self._validate_parameters(
            [
                ("volatility_multiplier", volatility_multiplier, float),
            ],
        )

        super().__init__(dataframe, window_size)

        self.hma_calculator = HullMovingAverageCalculator(
            dataframe=dataframe,
            window_size=window_size,
        )

        self.kc_calculator = KeltnerChannelCalculator(
            dataframe=dataframe,
            window_size=window_size,
            volatility_multiplier=volatility_multiplier,
        )

        self.cad_calculator = ChaikinAccumulationDistributionCalculator(
            dataframe=dataframe,
            window_size=window_size,
        )

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self._calculate_indicators()
        self._mark_trading_signals()
        self.dataframe.dropna(inplace=True)

    def _calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self.hma_calculator.calculate_hull_moving_average()
        self.kc_calculator.calculate_keltner_channel()
        self.cad_calculator.calculate_chaikin_accumulation_distribution_line()

    def _mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        long = (self.dataframe["adj close"] > self.dataframe["lkc_bound"]) & (
            self.dataframe["adl"] > self.dataframe["prev_adl"]
        )

        self.dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = (self.dataframe["adj close"] < self.dataframe["ukc_bound"]) & (
            self.dataframe["adl"] < self.dataframe["prev_adl"]
        )

        self.dataframe.loc[short, "signal"] = SHORT_SIGNAL
