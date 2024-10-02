import numpy as np
import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator

# ruff: noqa
# HEAVY WIP


class ElliotWavesCalculator(BaseCalculator):
    """Elliot Waves Calculator."""

    def __init__(
        self,
        dataframe: pd.DataFrame,
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

        # Calculate Fibonacci Lucas
        # for each entry in the dataframe
        fibonacci_lucas_sequence = self._calculate_fibonacci_lucas_sequence(
            len(self._dataframe),
        )

        # print(fibonacci_lucas_sequence)

    def _calculate_fibonacci_lucas_sequence(self, n: int) -> list[int]:
        """
        Calculate Fibonacci Lucas Sequence up until the end of price series.

        NOTE: we might use only Fibonacci; all work in progress.

        :param n: Number of Fibonacci Lucas numbers to calculate.
        :returns: Merged Fibonacci Lucas Sequence.
        """

        # Initialize sequences
        f_sequence = np.zeros(n, dtype=int)
        l_sequence = np.zeros(n, dtype=int)

        # Initialize first pairs
        f_sequence[0] = 1
        f_sequence[1] = 1
        l_sequence[0] = 1
        l_sequence[1] = 3

        # Loop in steps of 2 and
        # sum the last two values
        for i in range(2, n):
            f_sequence[i] = f_sequence[i - 1] + f_sequence[i - 2]
            l_sequence[i] = l_sequence[i - 1] + l_sequence[i - 2]

        # Merge the sequences removing duplicates
        return list(set(f_sequence) | set(l_sequence))
