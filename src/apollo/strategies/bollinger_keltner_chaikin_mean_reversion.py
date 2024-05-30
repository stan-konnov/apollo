from pandas import DataFrame

from apollo.calculations.bollinger_bands import BollingerBandsCalculator
from apollo.calculations.chaikin_accumulation_distribution import (
    ChaikinAccumulationDistributionCalculator,
)
from apollo.calculations.keltner_channel import KeltnerChannelCalculator
from apollo.calculations.mc_nicholl_moving_average import (
    McNichollMovingAverageCalculator,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy

"""
TODO: clean me
"""


class BollingerKeltnerChaikinMeanReversion(BaseStrategy):
    """
    Work in progress.

    Apply additional indicators from Kaufman:

    1. Keltner Channel
    2. Chaikin Oscillator
    3. Make BB more adaptive to volatility (Kaufman)
    4. Experiment with MACD + Chaikin Oscillator
    5. Experiment with McNicholl Moving Average for BB and KC
    6. Generally experiment with different MAs for BB, KC, and CO

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    Donadio and Ghosh, Algorithmic Trading, 2019, 1st ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        channel_sd_spread: float,
        volatility_multiplier: float,
    ) -> None:
        """
        Work in progress.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        :param channel_sd_spread: Standard deviation spread for Bollinger Bands.
        :param volatility_multiplier: ATR multiplier for Keltner Channel.
        """

        self._validate_parameters(
            [
                ("channel_sd_spread", channel_sd_spread, float),
                ("volatility_multiplier", volatility_multiplier, float),
            ],
        )

        super().__init__(dataframe, window_size)

        self.mnma_calculator = McNichollMovingAverageCalculator(
            dataframe=dataframe,
            window_size=window_size,
        )

        self.bb_calculator = BollingerBandsCalculator(
            dataframe=dataframe,
            window_size=window_size,
            channel_sd_spread=channel_sd_spread,
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

        self.mnma_calculator.calculate_mcnicholl_moving_average()
        self.kc_calculator.calculate_keltner_channel()
        self.bb_calculator.calculate_bollinger_bands()
        self.cad_calculator.calculate_chaikin_accumulation_distribution_line()

    def __mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        long = (
            (self.dataframe["adj close"] < self.dataframe["lb_band"])
            & (self.dataframe["lb_band"] > self.dataframe["lkc_bound"])
            & (self.dataframe["ub_band"] < self.dataframe["ukc_bound"])
        ) | (self.dataframe["adl"] < self.dataframe["adl_ema"])

        self.dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = (
            (self.dataframe["adj close"] > self.dataframe["ub_band"])
            & (self.dataframe["lb_band"] > self.dataframe["lkc_bound"])
            & (self.dataframe["ub_band"] < self.dataframe["ukc_bound"])
        ) | (self.dataframe["adl"] > self.dataframe["adl_ema"])

        self.dataframe.loc[short, "signal"] = SHORT_SIGNAL
