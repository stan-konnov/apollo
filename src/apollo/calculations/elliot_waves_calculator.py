from pandas import DataFrame

from apollo.calculations.base_calculator import BaseCalculator


class ElliotWavesCalculator(BaseCalculator):
    """Elliot Waves Calculator."""

    def __init__(
        self,
        dataframe: DataFrame,
        window_size: int,
        long_oscillator_period: int,
        short_oscillator_period: int,
    ) -> None:
        """
        Construct Elliot Waves Calculator.

        :param dataframe: Dataframe to calculate Elliot Waves for.
        :param window_size: Window size for rolling Elliot Waves calculation.
        :param long_oscillator_period: Long period for Elliot Waves Oscillator.
        :param short_oscillator_period: Short period for Elliot Waves Oscillator.
        """

        super().__init__(dataframe, window_size)

        self._long_oscillator_period = long_oscillator_period
        self._short_oscillator_period = short_oscillator_period
