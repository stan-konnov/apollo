import numpy as np
import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class ChaikinOscillatorCalculator(BaseCalculator):
    """
    Work in progress.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
        fast_ema_period: int,
        slow_ema_period: int,
    ) -> None:
        """
        Construct Chaikin Oscillator calculator.

        :param dataframe: Dataframe to calculate Chaikin Oscillator for.
        :param window_size: Window size for rolling Chaikin Oscillator calculation.
        :param fast_ema_period: Period for fast EMA calculation.
        :param slow_ema_period: Period for slow EMA calculation.
        """

        super().__init__(dataframe, window_size)

        self.fast_ema_period = fast_ema_period
        self.slow_ema_period = slow_ema_period

        self.accumulation_distribution_line: list[float] = []

    def calculate_chaikin_oscillator(self) -> None:
        """Calculate Chaikin Oscillator."""

        # Fill AD line array with N NaN, where N = window size
        self.accumulation_distribution_line = (
            np.full((1, self.window_size - 1), np.nan).flatten().tolist()
        )

        # Calculate rolling AD line
        self.dataframe["close"].rolling(self.window_size).apply(
            self._calc_adl,
            args=(self.dataframe,),
        )

        # Preserve AD line on the dataframe
        self.dataframe["adl"] = self.accumulation_distribution_line

        # Calculate fast ADL EMA
        fast_adl_ema = (
            self.dataframe["adl"]
            .ewm(
                alpha=1 / self.window_size,
                min_periods=self.fast_ema_period,
                adjust=False,
            )
            .mean()
        )

        # Calculate slow ADL EMA
        slow_adl_ema = (
            self.dataframe["adl"]
            .ewm(
                alpha=1 / self.window_size,
                min_periods=self.slow_ema_period,
                adjust=False,
            )
            .mean()
        )

        # Calculate Chaikin Oscillator
        self.dataframe["co"] = fast_adl_ema - slow_adl_ema

        # Drop ADL line from the dataframe
        self.dataframe.drop(columns=["adl"], inplace=True)

    def _calc_adl(self, series: pd.Series, dataframe: pd.DataFrame) -> float:
        """
        Work in progress.

        :param series: Series which is used for indexing out rolling window.
        :param dataframe: Original dataframe acting as a source of rolling window.
        :returns: Dummy float to satisfy Pandas' return value.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = dataframe.loc[series.index]

        # Calculate money flow multiplier
        # expressed as ((close - low) - (high - close)) / (high - low)
        money_flow_multiplier = (
            (rolling_df["close"] - rolling_df["low"])
            - (rolling_df["high"] - rolling_df["close"])
        ) / (rolling_df["high"] - rolling_df["low"])

        # Calculate money flow volume
        money_flow_volume = money_flow_multiplier * rolling_df["volume"]

        # Calculate AD line
        accumulation_distribution_line = money_flow_volume.cumsum()

        # Append last value to the AD line array
        self.accumulation_distribution_line.append(
            accumulation_distribution_line.iloc[-1],
        )

        # Return dummy float
        return 0.0
