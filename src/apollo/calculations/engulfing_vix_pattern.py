import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator
from apollo.settings import MISSING_DATA_PLACEHOLDER


class EngulfingVIXPatternCalculator(BaseCalculator):
    """
    Engulfing VIX Pattern Calculator.

    Calculates bullish and bearish engulfing pattern for VIX.

    NOTE: This calculator is identical to Engulfing Futures Pattern Calculator,
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
        Construct Engulfing VIX Pattern Calculator.

        :param dataframe: Dataframe to calculate Engulfing Pattern for.
        :param window_size: Window size for Engulfing Pattern calculation.

        NOTE: even though we accept window_size parameter,
        calculator does not perform any rolling calculations.
        """

        super().__init__(dataframe, window_size)

    def calculate_engulfing_vix_pattern(self) -> None:
        """Calculate Engulfing VIX Pattern."""

        # Since we are working with multiple
        # data sources, there is no guarantee that
        # the data is present for all the rows in the dataframe
        # We, therefore, can calculate only over present data points,
        # otherwise, the strategy using the results will drop missing rows

        # Mark engulfing patterns to the dataframe
        self._dataframe["vixep"] = self.NO_PATTERN

        # Initialize necessary columns with 0
        self._dataframe["vix_prev_open"] = 0.0
        self._dataframe["vix_prev_close"] = 0.0

        # Shift open and close prices only if the data is present
        self._dataframe.loc[
            self._dataframe["vix open"] != MISSING_DATA_PLACEHOLDER,
            "vix_prev_open",
        ] = self._dataframe["vix open"].shift(1)

        self._dataframe.loc[
            self._dataframe["vix close"] != MISSING_DATA_PLACEHOLDER,
            "vix_prev_close",
        ] = self._dataframe["vix close"].shift(1)

        # Calculate bullish engulfing
        self._dataframe.loc[
            (
                # Open at T is below the close at T-1
                # Candle opened below the close of the previous candle
                (self._dataframe["vix open"] < self._dataframe["vix_prev_open"])
                # Close at T is above the open at T-1
                # Candle closed above the open of the previous candle
                & (self._dataframe["vix close"] > self._dataframe["vix_prev_close"])
                # Close at T is above the open at T
                # Candle closed in positive territory
                & (self._dataframe["vix close"] > self._dataframe["vix open"])
            ),
            "vixep",
        ] = self.BULLISH_ENGULFING

        # Calculate bearish engulfing
        self._dataframe.loc[
            (
                # Open at T is above the close at T-1
                # Candle opened above the close of the previous candle
                (self._dataframe["vix open"] > self._dataframe["vix_prev_open"])
                # Close at T is below the open at T-1
                # Candle closed below the open of the previous candle
                & (self._dataframe["vix close"] < self._dataframe["vix_prev_close"])
                # Close at T is below the open at T
                # Candle closed in negative territory
                & (self._dataframe["vix close"] < self._dataframe["vix open"])
            ),
            "vixep",
        ] = self.BEARISH_ENGULFING

        # Drop unnecessary columns
        self._dataframe.drop(
            columns=["vix_prev_open", "vix_prev_close"],
            inplace=True,
        )
