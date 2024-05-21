import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class SupportResistanceCalculator(BaseCalculator):
    """
    Support and Resistance calculator.

    Calculates rolling support and resistance levels
    using a parametrized threshold of tolerance.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
        sup_count: float,
        res_count: float,
        sup_tolerance: float,
        res_tolerance: float,
    ) -> None:
        """
        Construct Support and Resistance calculator.

        :param dataframe: Dataframe to calculate support and resistance levels for.
        :param window_size: Window size for rolling support and resistance calculation.
        :param sup_count: Number of times support level is touched.
        :param res_count: Number of times resistance level is touched.
        :param sup_tolerance: Tolerance for support level calculation.
        :param res_tolerance: Tolerance for resistance level calculation.
        """

        super().__init__(dataframe, window_size)

        self.sup_count = sup_count
        self.res_count = res_count
        self.sup_tolerance = sup_tolerance
        self.res_tolerance = res_tolerance
