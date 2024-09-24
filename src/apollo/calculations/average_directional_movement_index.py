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

    def calculate_average_directional_movement_index(self) -> None:
        """Calculate rolling ADX via rolling DX and EMA."""

        # Precalculate previous low
        self._dataframe["prev_low"] = self._dataframe["adj low"].shift(1)

        # Precalculate previous high
        self._dataframe["prev_high"] = self._dataframe["adj high"].shift(1)

        # Precalculate Minus Directional Movement (MDM)
        self._dataframe["mdm"] = (
            self._dataframe["adj low"] - self._dataframe["prev_low"]
        )

        # Precalculate Plus Directional Movement (PDM)
        self._dataframe["pdm"] = (
            self._dataframe["adj high"] - self._dataframe["prev_high"]
        )
