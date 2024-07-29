from pandas import DataFrame

from apollo.calculations.wilders_swing_index import WildersSwingIndexCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy


class WildersSwingIndexTrendFollowing(BaseStrategy):
    """
    Wilder's Swing Index Trend Following.

    This strategy takes long positions when:

    * T-1 swing index reaches a high point, indicating that instrument is in uptrend.

    This strategy takes short positions when:

    * T-1 swing index reaches a low point, indicating that instrument is in downtrend.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
    ) -> None:
        """
        Construct Wilder's Swing Index Trend Following Strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
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
            self._dataframe["sp"] == self._wsi_calculator.HIGH_SWING_POINT,
            "signal",
        ] = LONG_SIGNAL

        self._dataframe.loc[
            self._dataframe["sp"] == self._wsi_calculator.LOW_SWING_POINT,
            "signal",
        ] = SHORT_SIGNAL
