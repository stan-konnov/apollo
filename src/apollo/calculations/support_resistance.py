import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class SupportResistanceCalculator(BaseCalculator):
    """
    Support and Resistance calculator.

    Calculates rolling support and resistance levels
    based on threshold of tolerance that defines the
    levels and number of times they are touched by the price.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
        sup_tolerance: float,
        res_tolerance: float,
        sup_touch_count: float,
        res_touch_count: float,
    ) -> None:
        """
        Construct Support and Resistance calculator.

        :param dataframe: Dataframe to calculate support and resistance levels for.
        :param window_size: Window size for rolling support and resistance calculation.
        :param sup_tolerance: Tolerance for support level calculation.
        :param res_tolerance: Tolerance for resistance level calculation.
        :param sup_touch_count: Number of times support level is touched.
        :param res_touch_count: Number of times resistance level is touched.
        """

        super().__init__(dataframe, window_size)

        self.sup_tolerance = sup_tolerance
        self.res_tolerance = res_tolerance
        self.sup_touch_count = sup_touch_count
        self.res_touch_count = res_touch_count
