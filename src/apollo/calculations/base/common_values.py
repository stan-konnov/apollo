from pandas import DataFrame


class CommonValuesCalculator:
    """
    Common Values Calculator class.

    Given there are multiple parts of the system
    that rely on some common precalculated values
    we isolate shared measurements in this separate class.
    """

    def __init__(self, dataframe: DataFrame) -> None:
        """
        Construct Common Values Calculator.

        :param dataframe: Dataframe to calculate common values for.
        """

        self._dataframe = dataframe

    def calculate_common_values(self) -> None:
        """Calculate common values shared across the system."""

        # Calculate previous close
        self._dataframe["prev_close"] = self._dataframe["adj close"].shift(1)
