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
    ELLIOT_WAVE_4: float = 4.0
    ELLIOT_WAVE_5: float = 5.0

    # Constants to
    # represent Elliot Waves Trends
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

        # Preserve elliot waves trend to the dataframe
        self._dataframe["ewt"] = self._elliot_waves_trend

        # Reset indices back to date
        self._dataframe.set_index("date", inplace=True)

    def _calc_elliot_waves_trend(self, series: pd.Series) -> float:
        """
        Calculate rolling Elliot Waves Trend.

        TODO: some experiments around the use
        of the golden ratio and inverse golden ratio required.

        if osc = highest(osc,period) and trend = 0 then trend = 1;
        if osc = lowest(osc, period) and trend = 0 then trend = -1;

        if lowest(osc,period) < 0 and trend = -1 and
        osc >  -1*trigger*lowest(osc,period) then trend = 1;
        if highest(osc,period) > 0 and trend = 1 and
        osc < -1*trigger*highest(osc,period) then trend = -1;

        :param series: Series which is used for indexing out rolling window.
        :returns: Dummy float to satisfy Pandas' return value.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[series.index]

        # Determine the highest and the
        # lowest EWO values within the window
        ewo_h = rolling_df["ewo"].max()
        ewo_l = rolling_df["ewo"].min()

        # Grab current EWO value
        current_ewo = rolling_df.iloc[-1]["ewo"]

        # Grab current trend value
        # NOTE: we use second to last index from rolling
        # window since we populate trend line exactly one step behind
        current_trend = self._elliot_waves_trend[rolling_df.index[-2]]

        # Determine if current trend is not set
        # NOTE: we check against NaN to facilitate for the first iteration
        no_current_trend = current_trend == self.NO_TREND or np.isnan(current_trend)

        # If the current trend is not set
        # and the current EWO is the highest EWO
        #
        # OR
        #
        # If the current EWO is below 0,
        # the current trend is downtrend
        # and current EWO is above lowest
        # multiplied by inverse golden ratio
        if (no_current_trend and current_ewo == ewo_h) or (
            current_ewo < 0
            and current_trend == self.DOWN_TREND
            and current_ewo > self.INVERSE_GOLDEN_RATIO * ewo_l
        ):
            # Mark the trend as uptrend
            self._elliot_waves_trend.append(self.UP_TREND)

        # If the current trend is not set
        # and the current EWO is the lowest EWO
        #
        # OR
        #
        # If the current EWO is above 0,
        # the current trend is uptrend
        # and current EWO is below highest
        # multiplied by inverse golden ratio
        elif (no_current_trend and current_ewo == ewo_l) or (
            current_ewo > 0
            and current_trend == self.UP_TREND
            and current_ewo < self.INVERSE_GOLDEN_RATIO * ewo_h
        ):
            # Mark the trend as downtrend
            self._elliot_waves_trend.append(self.DOWN_TREND)

        # Otherwise, keep
        # the trend as is
        else:
            self._elliot_waves_trend.append(self.NO_TREND)

        return 0.0
