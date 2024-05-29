from pandas import DataFrame

from apollo.calculations.bollinger_bands import BollingerBandsCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy


class BollingerBandsMeanReversion(BaseStrategy):
    """
    Work in progress.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    Donadio and Ghosh, Algorithmic Trading, 2019, 1st ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        channel_sd_spread: float,
    ) -> None:
        """
        Work in progress.

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

        self.bb_calculator = BollingerBandsCalculator(
            dataframe=dataframe,
            window_size=window_size,
            channel_sd_spread=channel_sd_spread,
        )

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self.__calculate_indicators()
        self.__mark_trading_signals()
        self.dataframe.dropna(inplace=True)

    def __calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self.bb_calculator.calculate_bollinger_bands()

    def __mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        long = self.dataframe["adj close"] <= self.dataframe["lb_band"]
        self.dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = self.dataframe["adj close"] >= self.dataframe["ub_band"]
        self.dataframe.loc[short, "signal"] = SHORT_SIGNAL
