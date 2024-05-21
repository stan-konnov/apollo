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
        sup_tolerance: float,
        res_tolerance: float,
    ) -> None:
        """
        Construct Distribution Moments calculator.

        :param dataframe: Dataframe to calculate support and resistance levels for.
        :param window_size: Window size for rolling support and resistance calculation.
        :param sup_tolerance: Tolerance for support level calculation.
        :param res_tolerance: Tolerance for resistance level calculation.
        """

        super().__init__(dataframe, window_size)

        self.sup_tolerance = sup_tolerance
        self.res_tolerance = res_tolerance
