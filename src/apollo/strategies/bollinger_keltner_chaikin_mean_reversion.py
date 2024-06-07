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


class BollingerKeltnerChaikinMeanReversion(BaseStrategy):
    """
    Bollinger Keltner Chaikin Mean Reversion.

    NOTE: this strategy uses McNicholl Moving Average as input
    for calculation of the Bollinger Bands and Keltner Channel
    in order to make the bands and the channel more responsive
    to the volatility of the instrument.

    This strategy takes long positions when:

    * Adjusted close is below the lower Bollinger Band,
    indicating that the instrument is oversold.

    * Accumulation Distribution Line is decreasing,
    indicating that the selling pressure is increasing
    and, therefore, has the potential to reverse back to the mean.

    This strategy takes short positions when:

    * Adjusted close is above the upper Bollinger Band,
    indicating that the instrument is overbought.

    * Accumulation Distribution Line is increasing,
    indicating that the buying pressure is increasing
    and, therefore, has the potential to reverse back to the mean.

    In both scenarios, the Bollinger Bands must be within the Keltner Channel
    to ensure that the instrument is not oversold/bought due to abnormal volatility.

    NOTE: we use Accumulation Distribution Line as OR condition
    in order to avoid unnecessary signal scrutiny
    that can lead to missed opportunities.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    Donadio and Ghosh, Algorithmic Trading, 2019, 1st ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        volatility_multiplier: float,
    ) -> None:
        """
        Construct Bollinger Keltner Chaikin Mean Reversion Strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        :param channel_sd_spread: Standard deviation spread for Bollinger Bands.
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

        self.__calculate_indicators()
        self.__mark_trading_signals()
        self.dataframe.dropna(inplace=True)

    def __calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self.hma_calculator.calculate_hull_moving_average()
        self.kc_calculator.calculate_keltner_channel()
        self.cad_calculator.calculate_chaikin_accumulation_distribution_line()

    def __mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        """I am actually trend following"""

        long = (self.dataframe["adj close"] > self.dataframe["lkc_bound"]) & (
            self.dataframe["adl"] > self.dataframe["prev_adl"]
        )

        self.dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = (self.dataframe["adj close"] < self.dataframe["ukc_bound"]) & (
            self.dataframe["adl"] < self.dataframe["prev_adl"]
        )

        self.dataframe.loc[short, "signal"] = SHORT_SIGNAL
