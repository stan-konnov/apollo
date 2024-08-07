import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class ConnersVixReversalCalculator(BaseCalculator):
    """Conners' VIX Reversal Calculator class."""

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct Conners' VIX Reversal Calculator.

        :param dataframe: Dataframe to calculate VIX reversals for.
        :param window_size: Window size for VIX reversals calculation.
        """

        super().__init__(dataframe, window_size)
