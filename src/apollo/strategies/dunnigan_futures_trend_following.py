from pandas import DataFrame

from apollo.calculations.dunnigan_futures_trend import DunniganFuturesTrendCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base.base_strategy import BaseStrategy
from apollo.strategies.base.volatility_adjusted_strategy import (
    VolatilityAdjustedStrategy,
)


class DunniganTrendFollowing(
    BaseStrategy,
    VolatilityAdjustedStrategy,
):
    """
    Work in progress.

    Massive work in progress:
    we might not even use Dunnigan, experimenting.

    I'm actually mean reversion.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
    ) -> None:
        """
        Work in progress.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        """

        BaseStrategy.__init__(self, dataframe, window_size)
        VolatilityAdjustedStrategy.__init__(self, dataframe, window_size)

        self._dft_calculator = DunniganFuturesTrendCalculator(
            dataframe=dataframe,
            window_size=window_size,
        )

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self._calculate_indicators()
        self._mark_trading_signals()
        self._dataframe.dropna(inplace=True)

    def _calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self._dft_calculator.calculate_dunnigan_futures_trend()

    def _mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        # NOTE: if this works, move it to calculations

        self._dataframe["prev_vix_close"] = self._dataframe["vix close"].shift(1)
        self._dataframe["prev_spf_close"] = self._dataframe["spf close"].shift(1)

        long = (self._dataframe["vix close"] < self._dataframe["prev_vix_close"]) & (
            self._dataframe["spf close"] > self._dataframe["prev_spf_close"]
        )

        self._dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = (self._dataframe["vix close"] > self._dataframe["prev_vix_close"]) & (
            self._dataframe["spf close"] < self._dataframe["prev_spf_close"]
        )

        self._dataframe.loc[short, "signal"] = SHORT_SIGNAL
