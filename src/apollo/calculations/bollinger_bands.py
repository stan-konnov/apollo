from pandas import DataFrame

from apollo.calculations.base_calculator import BaseCalculator


class BollingerBandsCalculator(BaseCalculator):
    """
    Bollinger Bands Calculator.

    Calculates the Bollinger Bands expressed
    as +/- N standard deviations from the simple moving average.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    Donadio and Ghosh, Algorithmic Trading, 2019, 1st ed.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        channel_sd_spread: float,
    ) -> None:
        """
        Construct Bollinger Bands calculator.

        :param dataframe: Dataframe to calculate Bollinger Bands for.
        :param window_size: Window size for rolling Bollinger Bands calculation.
        :param channel_sd_spread: Standard deviation spread for channel bounds.
        """

        super().__init__(dataframe, window_size)

        self.channel_sd_spread = channel_sd_spread
