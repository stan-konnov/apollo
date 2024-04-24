from pandas import DataFrame

from apollo.calculations.average_true_range import AverageTrueRangeCalculator
from apollo.calculations.key_reversals import KeyReversalsCalculator
from apollo.settings import LONG_SIGNAL, SHORT_SIGNAL
from apollo.strategies.base_strategy import BaseStrategy

# I am actually mean reversion!


class KeyReversalsTrendFollowing(BaseStrategy):
    """
    Key Reversals Trend Following.

    This strategy takes long positions when:

    * Up key reversal is detected -- price action is reversing from negative a trend.

    This strategy takes short positions when:

    * Down key reversal is detected -- price action is reversing from positive a trend.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
    ) -> None:
        """
        Construct Key Reversals Strategy.

        :param dataframe: Dataframe with price data.
        :param window_size: Size of the window for the strategy.
        """

        super().__init__(dataframe, window_size)

        self.kr_calculator = KeyReversalsCalculator(
            dataframe=dataframe,
            window_size=window_size,
        )

        self.at_calculator = AverageTrueRangeCalculator(
            dataframe=dataframe,
            window_size=window_size,
        )

    def model_trading_signals(self) -> None:
        """Model entry and exit signals."""

        self.__calculate_indicators()
        self.__mark_trading_signals()
        self.dataframe.dropna(inplace=True)

    def __calculate_indicators(self) -> None:
        """Calculate indicators necessary for the strategy."""

        self.kr_calculator.calculate_key_reversals()
        self.at_calculator.calculate_average_true_range()

    def __mark_trading_signals(self) -> None:
        """Mark long and short signals based on the strategy."""

        long = self.dataframe["kr"] == SHORT_SIGNAL
        self.dataframe.loc[long, "signal"] = LONG_SIGNAL

        short = (self.dataframe["kr"] == LONG_SIGNAL)
        self.dataframe.loc[short, "signal"] = SHORT_SIGNAL
