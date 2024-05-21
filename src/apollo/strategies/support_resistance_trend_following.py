from pandas import DataFrame

from apollo.calculations.support_resistance_touch_count import (
    SupportResistanceTouchCountCalculator,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy


class SupportResistanceTrendFollowing(BaseStrategy):
    """Work in progress."""

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        sup_tolerance: float,
        res_tolerance: float,
        sup_touch_threshold: int,
        res_touch_threshold: int,
    ) -> None:
        """Work in progress."""

        self._validate_parameters(
            [
                ("sup_tolerance", sup_tolerance, float),
                ("res_tolerance", res_tolerance, float),
                ("sup_touch_threshold", sup_touch_threshold, int),
                ("res_touch_threshold", res_touch_threshold, int),
            ],
        )

        super().__init__(dataframe, window_size)

        self.sup_touch_threshold = sup_touch_threshold
        self.res_touch_threshold = res_touch_threshold

        self.srtc_calculator = SupportResistanceTouchCountCalculator(
            dataframe=dataframe,
            window_size=window_size,
            sup_tolerance=sup_tolerance,
            res_tolerance=res_tolerance,
        )

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self.__calculate_indicators()
        self.__mark_trading_signals()
        self.dataframe.dropna(inplace=True)

    def __calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self.srtc_calculator.calculate_support_resistance_touch_points()

    def __mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        self.dataframe.loc[
            self.dataframe["rtc"] > self.res_touch_threshold,
            "signal",
        ] = LONG_SIGNAL

        self.dataframe.loc[
            self.dataframe["stc"] > self.sup_touch_threshold,
            "signal",
        ] = SHORT_SIGNAL
