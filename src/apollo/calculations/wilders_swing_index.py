import numpy as np
import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class WildersSwingIndexCalculator(BaseCalculator):
    """
    Wilder's Swing Index calculator.

    NOTE: the signal generation logic should be improved:

    # High/Low Swing Point:
    # Any day on which the ASI is higher/lower
    # than both the previous and the following day
    # Kaufman, Trading Systems and Methods, 2020, p.175

    Enter long when ASI crosses above HSPt-2
    Enter short when ASI crosses below LSPt-2
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
    ) -> None:
        """
        Construct Wilder's Swing Index calculator.

        :param dataframe: Dataframe to calculate Wilder's Swing Index for.
        :param window_size: Window size for rolling Wilder's Swing Index calculation.
        """

        super().__init__(dataframe, window_size)

        self._swing_points: list[float] = []

    def calculate_swing_index(self) -> None:
        """Calculate Wilder's Swing Index."""

        # Fill swing points array with N NaN, where N = window size
        self._swing_points = (
            np.full((1, self._window_size - 1), np.nan).flatten().tolist()
        )

        # Calculate rolling Swing Index
        self._dataframe["si"] = (
            self._dataframe["close"].rolling(self._window_size).apply(self.__calc_si)
        )

        # Calculate rolling Accumulated Swing Index
        self._dataframe["asi"] = (
            self._dataframe["close"].rolling(self._window_size).apply(self.__calc_asi)
        )

        # Calculate rolling Swing Points
        self._dataframe["close"].rolling(self._window_size).apply(self.__calc_sp)

        # Mark Swing Points into the dataframe
        self._dataframe["sp"] = self._swing_points

        # Since High and Low swing points are
        # based on the difference between three
        # consecutive ASI values, we need to shift
        # the SP column by one to get the correct signal
        self._dataframe["sp"] = self._dataframe["sp"].shift(1)

        # Drop SI column since we don't need it
        self._dataframe.drop(columns=["si"], inplace=True)

    def __calc_si(self, series: pd.Series) -> float:
        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[series.index]

        # Get open, high, low, close
        o: float = rolling_df.iloc[-1]["open"]
        h: float = rolling_df.iloc[-1]["high"]
        l: float = rolling_df.iloc[-1]["low"]  # noqa: E741
        c: float = rolling_df.iloc[-1]["close"]

        # Shift to get previous open and previous close
        prev_o = rolling_df["open"].shift(1).iloc[-1]
        prev_c = rolling_df["close"].shift(1).iloc[-1]

        # Calculate diffs between:
        # max(|Ht - Lt|, |Ht - Ct-1|, |Ct-1 - Lt|)
        # Kaufman, Trading Systems and Methods, 2020, p.174
        diffs = [h - prev_c, l - prev_c, h - l]

        # Bring to list of absolute floats
        abs_diffs = [abs(d) for d in diffs]

        # Get the highest value
        highest_value = max(abs_diffs)

        # Determine the index of the highest value
        # To decide which TR calculation we will be using
        highest_value_index = abs_diffs.index(highest_value)

        # Calculate K, the highest value of first 2 diffs
        highest_diff = max(abs_diffs)

        # Calculate TR using one of the methods based on highest value index
        true_range = self.__calc_tr(
            highest_value_index,
            h,
            l,
            prev_c,
            prev_o,
        )

        # Finally, calculate Swing Index:
        # K = highest of first two diffs, M = limit move
        # SI = 50 * ( ( (Ct - Ct-1) + 0.50(Ct - Ot) + 0.25(Ct-1 - Ot-1) ) / TRt ) * (K / M)  # noqa: ERA001, E501

        # Then calculate the actual index
        return (
            50
            * (
                ((c - prev_c) + (0.50 * (c - o)) + (0.25 * (prev_c - prev_o)))
                / true_range
            )
            * highest_diff
        )

    def __calc_asi(self, series: pd.Series) -> float:
        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[series.index]

        # Calculate ASI by summing
        # as we only need the last value
        return rolling_df["si"].sum()

    def __calc_sp(self, series: pd.Series) -> float:
        # High/Low Swing Point:
        # Any day on which the ASI is higher/lower
        # than both the previous and the following day
        # Kaufman, Trading Systems and Methods, 2020, p.175

        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[series.index]

        # Get the last 3 ASI entries
        last_three_asi = rolling_df.iloc[self._window_size - 3 :]["asi"]

        # Bring to list of floats
        last_three_asi = list(last_three_asi)

        # Unpack ASI values
        prev, curr, next = last_three_asi  # noqa: A001

        # If current ASI is higher than previous and next (HSP)
        if curr > prev and curr > next:
            # Append positive float to the list
            self._swing_points.append(1.0)

        # If current ASI is lower than previous and next (LSP)
        elif curr < prev and curr < next:
            # Append negative float to the list
            self._swing_points.append(-1.0)

        else:
            # Otherwise, append falsy float
            self._swing_points.append(0.0)

        # Return dummy value
        return 0.0

    def __calc_tr(
        self,
        diff_index: int,
        high: float,
        low: float,
        prev_close: float,
        prev_open: float,
    ) -> float:
        # Wilder's Swing Index uses adapted version of True Range
        # Therefore, we define several methods that we will
        # be using and then index them out based on logic
        # Kaufman, Trading Systems and Methods, 2020, p.175

        if diff_index == 0:
            return (
                abs(high - prev_close)
                - 0.50 * abs(low - prev_close)
                + 0.25 * abs(prev_close - prev_open)
            )

        if diff_index == 1:
            return (
                abs(low - prev_close)
                - 0.50 * abs(high - prev_close)
                + 0.25 * abs(prev_close - prev_open)
            )

        if diff_index == 2:  # noqa: PLR2004
            return abs(high - low) + 0.25 * abs(prev_close - prev_open)

        return 0.0
