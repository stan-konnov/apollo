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
        tolerance_level: float,
        touch_count_threshold: float,
    ) -> None:
        """Work in progress."""

        self._validate_parameters(
            [
                ("tolerance_level", tolerance_level, float),
                ("touch_count_threshold", touch_count_threshold, float),
            ],
        )

        super().__init__(dataframe, window_size)

        self.touch_count_threshold = touch_count_threshold

        self.srtc_calculator = SupportResistanceTouchCountCalculator(
            dataframe=dataframe,
            window_size=window_size,
            tolerance_level=tolerance_level,
        )

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self.__calculate_indicators()
        self.__mark_trading_signals()
        self.dataframe.dropna(inplace=True)

    def __calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self.srtc_calculator.calculate_support_resistance_touch_count()

    def __mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        self.dataframe.loc[
            self.dataframe["rtc"] > self.touch_count_threshold,
            "signal",
        ] = LONG_SIGNAL

        self.dataframe.loc[
            self.dataframe["stc"] > self.touch_count_threshold,
            "signal",
        ] = SHORT_SIGNAL
