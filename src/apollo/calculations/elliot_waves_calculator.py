import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class ElliotWavesCalculator(BaseCalculator):
    """Elliot Waves Calculator."""

    # Constant to
    # represent Golden Ratio
    GOLDEN_RATIO: float = 1.618

    # Constant to
    # represent Inverse Golden Ratio
    INVERSE_GOLDEN_RATIO: float = 0.618

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
        fast_oscillator_period: int,
        slow_oscillator_period: int,
    ) -> None:
        """
        Construct Elliot Waves Calculator.

        :param dataframe: Dataframe to calculate Elliot Waves for.
        :param window_size: Window size for Elliot Waves calculation.
        :param fast_oscillator_period: Fast period for Elliot Waves Oscillator.
        :param slow_oscillator_period: Slow period for Elliot Waves Oscillator.
        """

        super().__init__(dataframe, window_size)

        self._fast_oscillator_period = fast_oscillator_period
        self._slow_oscillator_period = slow_oscillator_period

    def calculate_elliot_waves(self) -> None:
        """Calculate rolling Elliot Waves."""

        # Precalculate the average
        # between high and low prices
        self._dataframe["high_low_avg"] = (
            self._dataframe["adj high"] + self._dataframe["adj low"]
        ) / 2

        # Calculate fast moving average
        # of the average between high and low
        self._dataframe["fast_hla_sma"] = (
            self._dataframe["high_low_avg"]
            .rolling(
                window=self._fast_oscillator_period,
                min_periods=self._fast_oscillator_period,
            )
            .mean()
        )

        # Calculate slow moving average
        # of the average between high and low
        self._dataframe["slow_hla_sma"] = (
            self._dataframe["high_low_avg"]
            .rolling(
                window=self._slow_oscillator_period,
                min_periods=self._slow_oscillator_period,
            )
            .mean()
        )

        # Calculate Elliot Waves Oscillator
        self._dataframe["ewo"] = (
            self._dataframe["fast_hla_sma"] - self._dataframe["slow_hla_sma"]
        )
