from pandas import DataFrame

from apollo.calculations.bollinger_bands import BollingerBandsCalculator
from apollo.calculations.chaikin_oscillator import ChaikinOscillatorCalculator
from apollo.calculations.keltner_channel import KeltnerChannelCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy


class BollingerBandsMeanReversion(BaseStrategy):
    """
    Work in progress.

    Apply additional indicators from Kaufman:

    1. Keltner Channel
    2. Chaikin Oscillator
    3. Make BB more adaptive to volatility (Kaufman)
    4. Experiment with MACD + Chaikin Oscillator

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    Donadio and Ghosh, Algorithmic Trading, 2019, 1st ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        channel_sd_spread: float,
        volatility_multiplier: float,
        fast_ema_period: float,
        slow_ema_period: float,
    ) -> None:
        """
        Work in progress.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        :param channel_sd_spread: Standard deviation spread for Bollinger Bands.
        :param volatility_multiplier: ATR multiplier for Keltner Channel.
        :param fast_ema_period: Period for fast ADL EMA calculation.
        :param slow_ema_period: Period for slow ADL EMA calculation.
        """

        self._validate_parameters(
            [
                ("channel_sd_spread", channel_sd_spread, float),
                ("volatility_multiplier", volatility_multiplier, float),
                ("fast_ema_period", fast_ema_period, float),
                ("slow_ema_period", slow_ema_period, float),
            ],
        )

        super().__init__(dataframe, window_size)

        self.kc_calculator = KeltnerChannelCalculator(
            dataframe=dataframe,
            window_size=window_size,
            volatility_multiplier=volatility_multiplier,
        )

        self.bb_calculator = BollingerBandsCalculator(
            dataframe=dataframe,
            window_size=window_size,
            channel_sd_spread=channel_sd_spread,
        )

        # NOTE: We cast fast and slow EMA periods to integers
        # as they are used as window sizes in the calculations.
        # Yet, the strategy consumes them as floats since parameter
        # optimizer is designed to create combinations of float values.
        self.co_calculator = ChaikinOscillatorCalculator(
            dataframe=dataframe,
            window_size=window_size,
            fast_ema_period=int(fast_ema_period),
            slow_ema_period=int(slow_ema_period),
        )

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self.__calculate_indicators()
        self.__mark_trading_signals()
        self.dataframe.dropna(inplace=True)

    def __calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self.kc_calculator.calculate_keltner_channel()
        self.bb_calculator.calculate_bollinger_bands()
        self.co_calculator.calculate_chaikin_oscillator()

    def __mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        long = (
            (self.dataframe["adj close"] < self.dataframe["lb_band"])
            & (self.dataframe["lb_band"] > self.dataframe["lkc_bound"])
            & (self.dataframe["ub_band"] < self.dataframe["ukc_bound"])
        ) | (self.dataframe["co"] > self.dataframe["adl"])

        self.dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = (
            (self.dataframe["adj close"] > self.dataframe["ub_band"])
            & (self.dataframe["lb_band"] > self.dataframe["lkc_bound"])
            & (self.dataframe["ub_band"] < self.dataframe["ukc_bound"])
        ) | (self.dataframe["co"] < self.dataframe["adl"])

        self.dataframe.loc[short, "signal"] = SHORT_SIGNAL
