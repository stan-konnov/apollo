from pandas import DataFrame


class BaseCalculator:
    """
    Base class for all calculators.

    Defines attributes shared by each child calculator.
    """

    def __init__(self, dataframe: DataFrame, window_size: int) -> None:
        """
        Construct Base calculator.

        :param dataframe: Dataframe to calculate values for.
        :param window_size: Window size for rolling calculation.
        """

        self._dataframe = dataframe
        self._window_size = window_size
