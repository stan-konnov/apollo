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
        s_oscillator_period: int,
        l_oscillator_period: int,
    ) -> None:
        """
        Construct Elliot Waves Calculator.

        :param dataframe: Dataframe to calculate Elliot Waves for.
        :param window_size: Window size for rolling Elliot Waves calculation.
        :param s_oscillator_period: Short period for Elliot Waves Oscillator.
        :param l_oscillator_period: Long period for Elliot Waves Oscillator.
        """

        super().__init__(dataframe, window_size)

        self._l_oscillator_period = l_oscillator_period
        self._s_oscillator_period = s_oscillator_period

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
                window=self._l_oscillator_period,
                min_periods=self._l_oscillator_period,
            )
            .mean()
        )

        # Calculate short moving average
        # of the average between high and low
        self._dataframe["short_hla_sma"] = (
            self._dataframe["high_low_avg"]
            .rolling(
                window=self._s_oscillator_period,
                min_periods=self._s_oscillator_period,
            )
            .mean()
        )

        # Calculate Elliot Waves Oscillator
        self._dataframe["elliot_waves_oscillator"] = (
            self._dataframe["short_hla_sma"] - self._dataframe["long_hla_sma"]
        )
