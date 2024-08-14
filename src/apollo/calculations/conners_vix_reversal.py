import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class ConnersVixExpansionContractionCalculator(BaseCalculator):
    """Conners' VIX Expansion Contraction Calculator."""

    # Constant to represent
    # VIX expansion to the upside
    UPSIDE_EXPANSION: float = 1.0

    # Constant to represent
    # VIX contraction to the downside
    DOWNSIDE_CONTRACTION: float = -1.0

    # Constant to represent
    # no significant VIX movement
    NO_SIGNIFICANT_MOVEMENT: float = 0.0

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct Conners' VIX Expansion Contraction Calculator.

        :param dataframe: Dataframe to calculate VIX expansion contraction for.
        :param window_size: Window size for VIX expansion and contraction calculation.
        """

        super().__init__(dataframe, window_size)

    def calculate_vix_expansion_contraction(self) -> None:
        """Calculate Conners' VIX Expansion Contraction."""

        # Precalculate VIX previous open and close
        self._dataframe["vix_prev_open"] = self._dataframe["vix open"].shift(1)
        self._dataframe["vix_prev_close"] = self._dataframe["vix close"].shift(1)

        # Calculate VIX expansion and
        # contraction and write to the dataframe
        self._dataframe["cvec"] = (
            self._dataframe["vix close"]
            .rolling(self._window_size)
            .apply(self._calc_cvec)
        )

        # Drop precalculated columns as we no longer need them
        self._dataframe.drop(
            columns=["vix_prev_open", "vix_prev_close"],
            inplace=True,
        )

    def _calc_cvec(self, series: pd.Series) -> float:
        """
        Calculate rolling VIX Expansion Contraction for a given window.

        :param series: Series which is used for indexing out rolling window.
        :returns: Latest calculated entry from processed window.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[series.index]

        # Get current VIX open and close
        curr_open = rolling_df["vix open"].iloc[-1]
        curr_close = rolling_df["vix close"].iloc[-1]

        # Get previous VIX open and close
        prev_open = rolling_df["vix_prev_open"].iloc[-1]
        prev_close = rolling_df["vix_prev_close"].iloc[-1]

        # Calculate VIX expansion to the upside
        if curr_open < prev_open and curr_close > prev_close and curr_close > curr_open:
            return self.UPSIDE_EXPANSION

        # Calculate VIX contraction to the downside
        if curr_open > prev_open and curr_close < prev_close and curr_close < curr_open:
            return self.DOWNSIDE_CONTRACTION

        return self.NO_SIGNIFICANT_MOVEMENT
