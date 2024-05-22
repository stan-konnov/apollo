import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class AbsolutePriceOscillatorCalculator(BaseCalculator):
    """
    Absolute Price Oscillator (APO) calculator.

    Calculates the APO based on the difference between
    short-term and long-term exponential moving averages.

    Donadio and Ghosh, Algorithmic Trading, 2019, 1st ed.
    """

    def __init__(self, dataframe: pd.DataFrame, window_size: int) -> None:
        """
        Construct APO calculator.

        :param dataframe: Dataframe to calculate APO for.
        :param window_size: Window size for rolling APO calculation.
        """

        super().__init__(dataframe, window_size)
