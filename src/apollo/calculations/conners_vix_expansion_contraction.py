import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator
from apollo.settings import MISSING_DATA_PLACEHOLDER

"""
TODO: this is indeed engulfing pattern,
      adapt docstrings and name,
      reference Conners' as inspiration.
"""


class ConnersVixExpansionContractionCalculator(BaseCalculator):
    """
    Conners' VIX Expansion Contraction Calculator.

    Connors VIX Expansion Contraction (CVEC) ultimately aims to
    capture VIX expansions to the upside and contractions to the downside.

    This is a modified version of Conners' VIX Reversals
    and does not follow the original logic to the letter.

    Expansions and contractions can be characterized as
    engulfing movements in either direction accompanied
    by increasing and decreasing VIX range, respectively.

    This is somewhat similar to bullish and bearish engulfing
    patterns, with the difference in the bearish pattern
    being that the close is lower than the open.

    Capturing downside movement as contraction in range
    is necessary to further reinforce the decrease in
    implied volatility and the potential for a reversal.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    # Constant to
    # represent no pattern
    NO_PATTERN: int = 0

    # Constant to represent
    # bullish engulfing pattern
    BULLISH_ENGULFING: int = 1

    # Constant to represent
    # bearish engulfing pattern
    BEARISH_ENGULFING: int = -1

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct Conners' VIX Expansion Contraction Calculator.

        :param dataframe: Dataframe to calculate VIX expansion contraction for.
        :param window_size: Window size for VIX expansion and contraction calculation.
        """

        super().__init__(dataframe, window_size)

    def calculate_vix_expansion_contraction(self) -> None:
        """Calculate Conners' VIX Expansion Contraction."""

        # Since we are working with multiple
        # data sources, there is no guarantee that
        # the data is present for all the rows in the dataframe
        # We, therefore, can calculate only over present data points
        # otherwise, the strategy using the results will drop missing rows

        # Mark engulfing patterns to the dataframe
        self._dataframe["vixep"] = self.NO_PATTERN

        # Initialize necessary columns with 0
        self._dataframe["vix_prev_open"] = 0
        self._dataframe["vix_prev_close"] = 0

        # Shift open and close prices only if the data is present
        self._dataframe.loc[
            self._dataframe["vix open"] != MISSING_DATA_PLACEHOLDER,
            "vix_prev_open",
        ] = self._dataframe["vix open"].shift(1)

        self._dataframe.loc[
            self._dataframe["vix close"] != MISSING_DATA_PLACEHOLDER,
            "vix_prev_close",
        ] = self._dataframe["vix close"].shift(1)

        self._dataframe.loc[
            (
                (self._dataframe["vix open"] < self._dataframe["vix_prev_open"])
                & (self._dataframe["vix close"] > self._dataframe["vix_prev_close"])
                & (self._dataframe["vix close"] > self._dataframe["vix open"])
            ),
            "vixep",
        ] = self.BULLISH_ENGULFING

        self._dataframe.loc[
            (
                (self._dataframe["vix open"] > self._dataframe["vix_prev_open"])
                & (self._dataframe["vix close"] < self._dataframe["vix_prev_close"])
                & (self._dataframe["vix close"] < self._dataframe["vix open"])
            ),
            "vixep",
        ] = self.BEARISH_ENGULFING
