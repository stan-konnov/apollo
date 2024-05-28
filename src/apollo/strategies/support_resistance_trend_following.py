from pandas import DataFrame

from apollo.calculations.support_resistance_touch_count import (
    SupportResistanceTouchCountCalculator,
)
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy


class SupportResistanceTrendFollowing(BaseStrategy):
    """
    Support Resistance Trend Following.

    This strategy takes long positions when:

    * Resistance touch count is above the threshold,
    indicating that price point is breaking through resistance level.

    This strategy takes short positions when:

    * Support touch count is above the threshold,
    indicating that price point is breaking through support level.

    Donadio and Ghosh, Algorithmic Trading, 2019, 1st ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        tolerance_threshold: float,
        touch_count_threshold: float,
    ) -> None:
        """
        Construct Support Resistance Trend Following strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        :param tolerance_threshold: Tolerance threshold for support-resistance levels.
        :param touch_count_threshold: Threshold for touch count to trigger the signal.
        """

        self._validate_parameters(
            [
                ("tolerance_threshold", tolerance_threshold, float),
                ("touch_count_threshold", touch_count_threshold, float),
            ],
        )

        super().__init__(dataframe, window_size)

        # NOTE: We consume touch count threshold as float since parameter
        # optimizer is designed to create combinations of float values.
        # Yet, it is used as an integer to trigger the signal.
        self.touch_count_threshold = touch_count_threshold

        self.srtc_calculator = SupportResistanceTouchCountCalculator(
            dataframe=dataframe,
            window_size=window_size,
            tolerance_threshold=tolerance_threshold,
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
