import numpy as np
import pandas as pd

from apollo.core.calculators.base_calculator import BaseCalculator


class ChaikinAccumulationDistributionCalculator(BaseCalculator):
    """
    Chaikin Accumulation Distribution Line Calculator.

    Chaikin Accumulation Distribution Line is a momentum indicator
    that determines the flow of liquidity into or out of an instrument.

    Chaikin Accumulation Distribution Line is calculated as follows:

    Calculate Money Flow Multiplier expressed as
    difference between close and low minus difference between
    high and close, divided by difference between high and low.

    Calculate Money Flow Volume expressed as
    product of Money Flow Multiplier and volume.

    Calculate Accumulation Distribution as cumulative sum of Money Flow Volume.

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
    ) -> None:
        """
        Construct Chaikin Accumulation Distribution Line Calculator.

        :param dataframe: Dataframe to calculate Chaikin AD Line for.
        :param window_size: Window size for rolling Chaikin AD Line calculation.
        """

        super().__init__(dataframe, window_size)

        self._accumulation_distribution_line: list[float] = []

    def calculate_chaikin_accumulation_distribution_line(self) -> None:
        """Calculate Chaikin Accumulation Distribution Line."""

        # Fill AD line array with N NaN, where N = window size
        self._accumulation_distribution_line = (
            np.full((1, self._window_size - 1), np.nan).flatten().tolist()
        )

        # Calculate rolling AD line
        self._dataframe["adj close"].rolling(self._window_size).apply(self._calc_adl)

        # Preserve AD line on the dataframe
        self._dataframe["adl"] = self._accumulation_distribution_line

        # Preserve previous AD line on the dataframe
        self._dataframe["prev_adl"] = self._dataframe["adl"].shift(1)

    def _calc_adl(self, series: pd.Series) -> float:
        """
        Calculate rolling Chaikin Accumulation Distribution.

        :param series: Series which is used for indexing out rolling window.
        :returns: Dummy float to satisfy Pandas' return value.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[series.index]

        # Calculate money flow multiplier
        money_flow_multiplier = (
            (rolling_df["adj close"] - rolling_df["adj low"])
            - (rolling_df["adj high"] - rolling_df["adj close"])
        ) / (rolling_df["adj high"] - rolling_df["adj low"])

        # Calculate money flow volume
        money_flow_volume = money_flow_multiplier * rolling_df["adj volume"]

        # Calculate AD value
        accumulation_distribution = money_flow_volume.cumsum()

        # Append last value to the AD line array
        self._accumulation_distribution_line.append(
            accumulation_distribution.iloc[-1],
        )

        # Return dummy float
        return 0.0
