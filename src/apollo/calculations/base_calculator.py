from pandas import DataFrame


class BaseCalculator:
    """
    Base class for all calculators.

    Defines attributes shared by each child calculator.
    """

    def __init__(self, dataframe: DataFrame, window_size: int | None = None) -> None:
        """
        Construct Base calculator.

        :param dataframe: DataFrame to calculate values for.
        :param window_size: Window size for rolling calculation.

        NOTE: window_size is optional for some calculators.
        """

        self.dataframe = dataframe
        self.window_size = window_size
