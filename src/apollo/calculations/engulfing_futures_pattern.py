import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator
from apollo.settings import MISSING_DATA_PLACEHOLDER


class EngulfingFuturesPatternCalculator(BaseCalculator):
    """
    Engulfing Futures Pattern Calculator.

    Calculates bullish and bearish engulfing pattern for S&P 500 Futures.

    NOTE: This calculator is identical to Engulfing VIX Pattern Calculator,
    yet, is kept separate to maintain possibility of extending one
    or the other with additional functionality in the future.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    # Constant to
    # represent no pattern
    NO_PATTERN: float = 0.0

    # Constant to represent
    # bullish engulfing pattern
    BULLISH_ENGULFING: float = 1.0

    # Constant to represent
    # bearish engulfing pattern
    BEARISH_ENGULFING: float = -1.0

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct Engulfing Futures Pattern Calculator.

        :param dataframe: Dataframe to calculate Engulfing Pattern for.
        :param window_size: Size of the window for Engulfing Pattern calculation.

        NOTE: even though we accept window_size parameter,
        calculator does not perform any rolling calculations.
        """

        super().__init__(dataframe, window_size)

    def calculate_engulfing_futures_pattern(self) -> None:
        """Calculate Engulfing Futures Pattern."""

        # Since we are working with multiple
        # data sources, there is no guarantee that
        # the data is present for all the rows in the dataframe
        # We, therefore, can calculate only over present data points,
        # otherwise, the strategy using the results will drop missing rows

        # Mark engulfing patterns to the dataframe
        self._dataframe["spfep"] = self.NO_PATTERN

        # Initialize necessary columns with 0
        self._dataframe["spf_prev_open"] = 0
        self._dataframe["spf_prev_close"] = 0

        # Shift open and close prices only if the data is present
        self._dataframe.loc[
            self._dataframe["spf open"] != MISSING_DATA_PLACEHOLDER,
            "spf_prev_open",
        ] = self._dataframe["spf open"].shift(1)

        self._dataframe.loc[
            self._dataframe["spf close"] != MISSING_DATA_PLACEHOLDER,
            "spf_prev_close",
        ] = self._dataframe["spf close"].shift(1)

        self._dataframe.loc[
            (
                (self._dataframe["spf open"] < self._dataframe["spf_prev_open"])
                & (self._dataframe["spf close"] > self._dataframe["spf_prev_close"])
                & (self._dataframe["spf close"] > self._dataframe["spf open"])
            ),
            "spfep",
        ] = self.BULLISH_ENGULFING

        self._dataframe.loc[
            (
                (self._dataframe["spf open"] > self._dataframe["spf_prev_open"])
                & (self._dataframe["spf close"] < self._dataframe["spf_prev_close"])
                & (self._dataframe["spf close"] < self._dataframe["spf open"])
            ),
            "spfep",
        ] = self.BEARISH_ENGULFING

        # Drop unnecessary columns
        self._dataframe.drop(
            columns=["spf_prev_open", "spf_prev_close"],
            inplace=True,
        )
