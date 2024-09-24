import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class AverageDirectionalMovementIndexCalculator(BaseCalculator):
    """
    Average Directional Movement Index Calculator.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    Wilder, "Selection and Direction", Technical Analysis in Commodities, 1980.
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct ADX Calculator.

        :param dataframe: Dataframe to calculate ADX for.
        :param window_size: Window size for rolling ADX calculation.
        """

        super().__init__(dataframe, window_size)
