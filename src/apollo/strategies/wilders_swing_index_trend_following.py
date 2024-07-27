from pandas import DataFrame

from apollo.calculations.wilders_swing_index import WildersSwingIndexCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy


class WildersSwingIndexTrendFollowing(BaseStrategy):
    """WIP."""

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
    ) -> None:
        """
        Construct Wilder's Swing Index Mean Reversion Strategy.

        WIP.
        """

        super().__init__(dataframe, window_size)

        self._wsi_calculator = WildersSwingIndexCalculator(
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

        self._wsi_calculator.calculate_swing_index()

    def _mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        self._dataframe.loc[
            self._dataframe["sp"] == 1,
            "signal",
        ] = LONG_SIGNAL

        self._dataframe.loc[
            self._dataframe["sp"] == -1,
            "signal",
        ] = SHORT_SIGNAL
