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
    ELLIOT_WAVE_3: float = 3.0
    ELLIOT_WAVE_4: float = 4.0
    ELLIOT_WAVE_5: float = 5.0

    # Constants to
    # represent Elliot Waves Trends
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

        # Declare variables for highest
        # oscillator and high-low average
        self._ewo_h_1: float = -np.inf
        self._ewo_h_2: float = -np.inf
        self._hla_h_1: float = -np.inf
        self._hla_h_2: float = -np.inf

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
            self._calc_elliot_waves_trend,
        )

        # Preserve Elliot Waves Trend to the dataframe
        self._dataframe["ewt"] = self._elliot_waves_trend

        # Shift Elliot Waves Trend by one observation
        self._dataframe["prev_ewt"] = self._dataframe["ewt"].shift(1)

        # Calculate rolling Elliot Waves
        self._dataframe["adj close"].rolling(self._window_size).apply(
            self._calc_elliot_waves,
        )

        # Preserve Elliot Waves to the dataframe
        self._dataframe["ew"] = self._elliot_waves

        # Shift Elliot Waves by one observation
        self._dataframe["prev_ew"] = self._dataframe["ew"].shift(1)

        # Reset indices back to date
        self._dataframe.set_index("date", inplace=True)

    def _calc_elliot_waves_trend(self, series: pd.Series) -> float:
        """
        Calculate rolling Elliot Waves Trend.

        TODO: some experiments around retracement logic required.

        :param series: Series which is used for indexing out rolling window.
        :returns: Dummy float to satisfy Pandas' return value.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[series.index]

        # Declare variable
        # for current trend
        curr_trend = None

        # Determine the highest and the
        # lowest EWO values within the window
        ewo_h = rolling_df["ewo"].max()
        ewo_l = rolling_df["ewo"].min()

        # Grab current EWO value
        current_ewo = rolling_df.iloc[-1]["ewo"]

        # Grab previous trend value
        # NOTE: we use second to last index from rolling
        # window since we populate trend line up to one step behind
        prev_trend = self._elliot_waves_trend[rolling_df.index[-2]]

        # Determine if previous trend is not set
        # NOTE: we check against NaN to facilitate for the first iteration
        no_prev_trend = prev_trend == self.NO_VALUE or np.isnan(prev_trend)

        # If the previous trend is not set
        # and the current EWO is the highest EWO
        if no_prev_trend and current_ewo == ewo_h:
            # Mark the trend as uptrend
            curr_trend = self.UP_TREND

        # If the current EWO is below 0,
        # the previous trend is downtrend
        # and current EWO retraces back up
        # to one golden ratio from lowest
        if (
            current_ewo < 0
            and prev_trend == self.DOWN_TREND
            and current_ewo > self.GOLDEN_RATIO * ewo_l
        ):
            # Mark the trend as uptrend
            curr_trend = self.UP_TREND

        # If the previous trend is not set
        # and the current EWO is the lowest EWO
        if no_prev_trend and current_ewo == ewo_l:
            # Mark the trend as downtrend
            curr_trend = self.DOWN_TREND

        # If the current EWO is above 0,
        # the previous trend is uptrend
        # and current EWO retraces back down
        # to one golden ratio from the highest
        if (
            current_ewo > 0
            and prev_trend == self.UP_TREND
            and current_ewo < self.GOLDEN_RATIO * ewo_h
        ):
            # Mark the trend as downtrend
            curr_trend = self.DOWN_TREND

        # Append the current trend to the
        # trend line or resolve to no trend
        self._elliot_waves_trend.append(curr_trend or self.NO_VALUE)

        return 0.0

    def _calc_elliot_waves(self, series: pd.Series) -> float:  # noqa: C901
        """
        Calculate rolling Elliot Waves Trend.

        TODO: look into if this can be
        combined with previous rolling method.

        :param series: Series which is used for indexing out rolling window.
        :returns: Dummy float to satisfy Pandas' return value.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[series.index]

        # Declare variable
        # for current Elliot Wave
        curr_wave = None

        # Determine the highest
        # high-low average within the window
        hla_h = rolling_df["high_low_avg"].max()

        # Grab current and previous trend values
        curr_trend = rolling_df.iloc[-1]["ewt"]
        prev_trend = rolling_df.iloc[-2]["prev_ewt"]

        # Grab current EWO value
        curr_ewo = rolling_df.iloc[-1]["ewo"]

        # Grab current high-low average value
        curr_hla = rolling_df.iloc[-1]["high_low_avg"]

        # Test for beginning of wave 3:
        #
        # If the current trend is uptrend
        # and the previous trend was downtrend
        if curr_trend == self.UP_TREND and prev_trend == self.DOWN_TREND:
            # Mark the wave as Elliot Wave 3
            curr_wave = self.ELLIOT_WAVE_3

            # Resolve EWO high 1
            # to the current EWO
            self._ewo_h_1 = curr_ewo

            # Resolve high-low average high 1
            # to the current high-low average
            self._hla_h_1 = curr_hla

        # If the current wave is Elliot Wave 3
        if curr_wave == self.ELLIOT_WAVE_3:
            # If the current EWO
            # higher than the EWO high 1
            if curr_ewo > self._ewo_h_1:
                # Resolve EWO high 1
                # to the current EWO
                self._ewo_h_1 = curr_ewo

            # If the current high-low average
            # higher than the high-low average 1
            if curr_hla > self._hla_h_1:
                # Resolve high-low average high 1
                # to the current high-low average
                self._hla_h_1 = curr_hla

        # Test for beginning of wave 4:
        #
        # If oscillator is equal or below 0
        # and the current trend is uptrend
        if curr_ewo <= 0 and curr_trend == self.UP_TREND:
            # Mark the wave as Elliot Wave 4
            curr_wave = self.ELLIOT_WAVE_4

        # Test for beginning of wave 5:
        #
        # If the current wave is Elliot Wave 4
        # and the current high-low average is highest
        # abd oscillator is equal or above 0
        if curr_wave == self.ELLIOT_WAVE_4 and curr_hla == hla_h and curr_ewo >= 0:
            # Mark the wave as Elliot Wave 5
            curr_wave = self.ELLIOT_WAVE_5

            # Resolve EWO high 2
            # to the current EWO
            self._ewo_h_2 = curr_ewo

            # Resolve high-low average high 2
            # to the current high-low average
            self._hla_h_2 = curr_hla

        # If the current wave is Elliot Wave 5
        if curr_wave == self.ELLIOT_WAVE_5:
            # If the current EWO
            # higher than the EWO high 2
            if curr_ewo > self._ewo_h_2:
                # Resolve EWO high 2
                # to the current EWO
                self._ewo_h_2 = curr_ewo

            # If the current high-low average
            # higher than the high-low average 2
            if curr_hla > self._hla_h_2:
                # Resolve high-low average high 2
                # to the current high-low average
                self._hla_h_2 = curr_hla

        # Test for wave 5 turning into wave 3
        #
        # If the current wave is Elliot Wave 5
        # and high-low average high 2 is higher than current
        # and current trend is uptrend
        if (
            curr_wave == self.ELLIOT_WAVE_5
            and self._hla_h_2 > curr_hla
            and curr_trend == self.UP_TREND
        ):
            # Mark the wave as Elliot Wave 3
            curr_wave = self.ELLIOT_WAVE_3

            # Resolve EWO high 1
            # to the EWO high 2
            self._ewo_h_1 = self._ewo_h_2

            # Resolve high-low average high 1
            # to the high-low average 2
            self._hla_h_1 = self._hla_h_2

            # Resolve EWO high 2
            # to negative ignorable
            self._ewo_h_2 = -np.inf

            # Resolve high-low average high 2
            # to negative ignorable
            self._hla_h_2 = -np.inf

        # Test for wave 3 down within wave 5
        #
        # If the current wave is Elliot Wave 5
        # and current trend is downtrend
        if curr_wave == self.ELLIOT_WAVE_5 and curr_trend == self.DOWN_TREND:
            # Mark the wave as Elliot Wave 3
            curr_wave = self.ELLIOT_WAVE_3

            # Resolve EWO high 1
            # to negative ignorable
            self._ewo_h_1 = -np.inf

            # Resolve high-low average high 1
            # to negative ignorable
            self._hla_h_1 = -np.inf

            # Resolve EWO high 2
            # to negative ignorable
            self._ewo_h_2 = -np.inf

            # Resolve high-low average high 2
            # to negative ignorable
            self._hla_h_2 = -np.inf

        # Append the wave to the
        # wave line or resolve to no wave
        self._elliot_waves.append(curr_wave or self.NO_VALUE)

        return 0.0
