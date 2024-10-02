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

    def calculate_elliot_waves(self) -> None:
        """Calculate rolling Elliot Waves."""

        # Precalculate the average
        # between high and low prices
        self._dataframe["high_low_avg"] = (
            self._dataframe["adj high"] + self._dataframe["adj low"]
        ) / 2

        # Calculate long moving average
        # of the average between high and low
        self._dataframe["long_hla_sma"] = (
            self._dataframe["high_low_avg"]
            .rolling(
                window=self._long_oscillator_period,
                min_periods=self._long_oscillator_period,
            )
            .mean()
        )

        # Calculate short moving average
        # of the average between high and low
        self._dataframe["short_hla_sma"] = (
            self._dataframe["high_low_avg"]
            .rolling(
                window=self._short_oscillator_period,
                min_periods=self._short_oscillator_period,
            )
            .mean()
        )

        # Calculate Elliot Waves Oscillator
        self._dataframe["elliot_waves_oscillator"] = (
            self._dataframe["short_hla_sma"] - self._dataframe["long_hla_sma"]
        )
