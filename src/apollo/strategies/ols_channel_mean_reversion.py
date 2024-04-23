from pandas import DataFrame

from apollo.calculations.price_channels import PriceChannelsCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base import BaseStrategy


class OrdinaryLeastSquaresChannelMeanReversion(BaseStrategy):
    """OrdinaryLeastSquaresChannelsMeanReversion."""

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        channel_sd_spread: float,
    ) -> None:
        """
        Construct.

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

        self.pc_calculator = PriceChannelsCalculator(
            dataframe,
            window_size,
            channel_sd_spread,
        )


    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self.__calculate_indicators()
        self.__mark_trading_signals()
        self.dataframe.dropna(inplace=True)


    def __calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self.pc_calculator.calculate_price_channels()


    def __mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        long = (
            (self.dataframe["adj close"] <= self.dataframe["l_bound"]) &
            (self.dataframe["slope"] <= self.dataframe["prev_slope"])
        )
        self.dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = (
            (self.dataframe["adj close"] >= self.dataframe["u_bound"]) &
            (self.dataframe["slope"] >= self.dataframe["prev_slope"])
        )
        self.dataframe.loc[short, "signal"] = SHORT_SIGNAL
