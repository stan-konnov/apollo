from pandas import DataFrame

from apollo.calculators.wilders_swing_index import WildersSwingIndexCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base.base_strategy import BaseStrategy
from apollo.strategies.base.volatility_adjusted_strategy import (
    VolatilityAdjustedStrategy,
)


class WildersSwingIndexTrendFollowing(
    BaseStrategy,
    VolatilityAdjustedStrategy,
):
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
        weighted_tr_multiplier: float,
    ) -> None:
        """
        Construct Wilder's Swing Index Trend Following Strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        :param weighted_tr_multiplier: Multiplier for weighted True Range calculation.
        """

        self._validate_parameters(
            [
                ("weighted_tr_multiplier", weighted_tr_multiplier, float),
            ],
        )

        BaseStrategy.__init__(self, dataframe, window_size)
        VolatilityAdjustedStrategy.__init__(self, dataframe, window_size)

        self._wsi_calculator = WildersSwingIndexCalculator(
            dataframe=dataframe,
            window_size=window_size,
            weighted_tr_multiplier=weighted_tr_multiplier,
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
