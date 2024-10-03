import numpy as np
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

    # Constants to
    # represent Elliot Waves
    ELLIOT_WAVE_3: float = 3.0
    ELLIOT_WAVE_5: float = 5.0

    # Constants to
    # represent Elliot Trends
    NO_TREND: float = 0.0
    UP_TREND: float = 1.0
    DOWN_TREND: float = -1.0

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

        self._ewo_l: float = 0.0
        self._ewo_h: float = 0.0

        self._elliot_trend: list[float] = []

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

        # Fill trend line array with N NaN, where N = window size
        self._elliot_trend = (
            np.full((1, self._window_size - 1), np.nan).flatten().tolist()
        )

    def _calc_elliot_waves(self, series: pd.Series) -> float:
        """
        Calculate rolling Elliot Waves.

        :param series: Series which is used for indexing out rolling window.
        :returns: Dummy float to satisfy Pandas' return value.
        """

        # Slice out a chunk of dataframe to work with
        _rolling_df = self._dataframe.loc[series.index]

        # Determine the highest and the
        # lowest EWO values within the window
        _ewo_h = _rolling_df["ewo"].max()
        _ewo_l = _rolling_df["ewo"].min()

        return 0.0
