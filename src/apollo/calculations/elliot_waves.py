import numpy as np
import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class ElliotWavesCalculator(BaseCalculator):
    """Elliot Waves Calculator."""

    # Constant to
    # represent Golden Ratio
    GOLDEN_RATIO: float = 1.618

    # Constant to
    # represent no value
    NO_VALUE: float = 0.0

    # Constants to
    # represent Elliot Waves
    ELLIOT_WAVE_1: float = 1.0
    ELLIOT_WAVE_2: float = 2.0
    ELLIOT_WAVE_3: float = 3.0
    ELLIOT_WAVE_4: float = 4.0

    # Constants to
    # represent Elliot Waves Trends
    UP_TREND: float = 1.0
    DOWN_TREND: float = -1.0

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
        fast_oscillator_period: float,
        slow_oscillator_period: float,
    ) -> None:
        """
        Construct Elliot Waves Calculator.

        TODO: massive comments improvement.

        :param dataframe: Dataframe to calculate Elliot Waves for.
        :param window_size: Window size for Elliot Waves calculation.
        :param fast_oscillator_period: Fast period for Elliot Waves Oscillator.
        :param slow_oscillator_period: Slow period for Elliot Waves Oscillator.
        """

        super().__init__(dataframe, window_size)

        self._fast_oscillator_period = fast_oscillator_period
        self._slow_oscillator_period = slow_oscillator_period

        # Declare variables for
        # Elliot Waves Oscillator peaks
        self._ewo_l_peaks: list[float] = []
        self._ewo_h_peaks: list[float] = []

        # Declare variables for
        # Elliot Waves and Elliot Waves Trend
        self._elliot_waves: list[float] = []
        self._elliot_waves_trend: list[float] = []

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
                window=int(self._fast_oscillator_period),
                min_periods=int(self._fast_oscillator_period),
            )
            .mean()
        )

        # Calculate slow moving average
        # of the average between high and low
        self._dataframe["slow_hla_sma"] = (
            self._dataframe["high_low_avg"]
            .rolling(
                window=int(self._slow_oscillator_period),
                min_periods=int(self._slow_oscillator_period),
            )
            .mean()
        )

        # Calculate Elliot Waves Oscillator
        self._dataframe["ewo"] = (
            self._dataframe["fast_hla_sma"] - self._dataframe["slow_hla_sma"]
        )

        # Calculate EWO SMA
        self._dataframe["ewo_sma"] = (
            self._dataframe["ewo"]
            .rolling(
                window=self._window_size,
                min_periods=self._window_size,
            )
            .mean()
        )

        # Fill peak lines array with N NaN, where N = window size
        self._ewo_l_peaks = (
            np.full((1, self._window_size - 1), np.nan).flatten().tolist()
        )

        self._ewo_h_peaks = (
            np.full((1, self._window_size - 1), np.nan).flatten().tolist()
        )

        # Fill wave line array with N NaN, where N = window size
        self._elliot_waves = (
            np.full((1, self._window_size - 1), np.nan).flatten().tolist()
        )

        # Fill trend line array with N NaN, where N = window size
        self._elliot_waves_trend = (
            np.full((1, self._window_size - 1), np.nan).flatten().tolist()
        )

        # Reset indices to integer to
        # facilitate access of previous trend
        self._dataframe.reset_index(inplace=True)

        # Calculate rolling Elliot Waves Trend
        self._dataframe["adj close"].rolling(self._window_size).apply(
            self._calc_elliot_waves,
        )

        # Preserve Elliot Waves to the dataframe
        self._dataframe["ew"] = self._elliot_waves

        # Preserve peaks to the dataframe
        self._dataframe["ewo_lp"] = self._ewo_l_peaks
        self._dataframe["ewo_hp"] = self._ewo_h_peaks

        # Reset indices back to date
        self._dataframe.set_index("date", inplace=True)

    def _calc_elliot_waves(self, series: pd.Series) -> float:
        """
        Calculate rolling Elliot Waves.

        :param series: Series which is used for indexing out rolling window.
        :returns: Dummy float to satisfy Pandas' return value.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[series.index]

        # Declare variable
        # for current wave
        curr_wave = None

        # Declare variable
        # for current trend
        curr_trend = None

        # Determine the highest and the
        # lowest EWO values within the window
        ewo_h = rolling_df["ewo"].max()
        ewo_l = rolling_df["ewo"].min()

        # Grab current EWO value
        curr_ewo = rolling_df.iloc[-1]["ewo"]

        # Grab current EWO SMA value
        curr_ewo_sma = rolling_df.iloc[-1]["ewo_sma"]

        # Grab previous trend value
        # NOTE: we use second to last index from rolling
        # window since we populate trend line up to one step behind
        prev_trend = self._elliot_waves_trend[rolling_df.index[-2]]

        # Determine if previous trend is not set
        # NOTE: we check against NaN to facilitate for the first iteration
        no_prev_trend = prev_trend == self.NO_VALUE or np.isnan(prev_trend)

        # If the previous trend is not set
        # and the current EWO is the highest EWO
        if no_prev_trend and curr_ewo == ewo_h:
            # Mark the trend as uptrend
            curr_trend = self.UP_TREND

        # If the current EWO is below 0,
        # the previous trend is downtrend
        # and current EWO retraces back up
        # to one golden ratio from lowest
        if (
            curr_ewo < curr_ewo_sma
            and prev_trend == self.DOWN_TREND
            and curr_ewo > self.GOLDEN_RATIO * ewo_l
        ):
            # Mark the trend as uptrend
            curr_trend = self.UP_TREND

        # If the previous trend is not set
        # and the current EWO is the lowest EWO
        if no_prev_trend and curr_ewo == ewo_l:
            # Mark the trend as downtrend
            curr_trend = self.DOWN_TREND

        # If the current EWO is above 0,
        # the previous trend is uptrend
        # and current EWO retraces back down
        # to one golden ratio from the highest
        if (
            curr_ewo > curr_ewo_sma
            and prev_trend == self.UP_TREND
            and curr_ewo < self.GOLDEN_RATIO * ewo_h
        ):
            # Mark the trend as downtrend
            curr_trend = self.DOWN_TREND

        # Now that we have a trend
        # we can determine the wave

        """
        TODO: Not beginning, but end?
        """

        # Test for beginning of wave 1:
        # If oscillator is above average
        # and the current trend is downtrend
        if curr_ewo > ewo_l and curr_trend == self.DOWN_TREND:
            # Mark the wave as Elliot Wave 1
            curr_wave = self.ELLIOT_WAVE_1

        # Test for beginning of wave 2:
        # If oscillator is below average
        # and the current trend is downtrend
        if curr_ewo < ewo_h and curr_trend == self.DOWN_TREND:
            # Mark the wave as Elliot Wave 2
            curr_wave = self.ELLIOT_WAVE_2

        # Test for beginning of wave 3:
        # If oscillator is below average
        # and the current trend is uptrend
        if curr_ewo < ewo_h and curr_trend == self.UP_TREND:
            # Mark the wave as Elliot Wave 3
            curr_wave = self.ELLIOT_WAVE_3

        # Test for beginning of wave 4:
        # If oscillator is above average
        # and the current trend is uptrend
        if curr_ewo > ewo_l and curr_trend == self.UP_TREND:
            # Mark the wave as Elliot Wave 4
            curr_wave = self.ELLIOT_WAVE_4

        # Append local oscillator peaks
        self._ewo_l_peaks.append(ewo_l)
        self._ewo_h_peaks.append(ewo_h)

        # Append the wave to the
        # wave line or resolve to no wave
        self._elliot_waves.append(curr_wave or self.NO_VALUE)

        # Append the current trend to the
        # trend line or resolve to no trend
        self._elliot_waves_trend.append(curr_trend or self.NO_VALUE)

        return 0.0
