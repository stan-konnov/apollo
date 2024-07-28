import numpy as np
import pandas as pd

from apollo.calculations.base_calculator import BaseCalculator


class WildersSwingIndexCalculator(BaseCalculator):
    """
    Wilder's Swing Index calculator.

    Wilder's Swing Index is an event-driven
    indicator that captures High and Low swing points.

    The High and Low swing points are based
    on the difference between three consecutive
    ASI values, where ASI is the sum of the Swing Index values.

    Kaufman, Trading Systems and Methods, 2020, p.174
    """

    # Constant to represent low swing point
    LOW_SWING_POINT: float = -1.0

    # Constant to represent high swing point
    HIGH_SWING_POINT: float = 1.0

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

        # Shift to get previous open and previous close
        self._dataframe["prev_open"] = self._dataframe["adj open"].shift(1)
        self._dataframe["prev_close"] = self._dataframe["adj close"].shift(1)

        # Calculate rolling Swing Index
        self._dataframe["si"] = (
            self._dataframe["adj close"].rolling(self._window_size).apply(self._calc_si)
        )

        # Calculate rolling Accumulated Swing Index
        self._dataframe["asi"] = (
            self._dataframe["adj close"]
            .rolling(self._window_size)
            .apply(self._calc_asi)
        )

        # Calculate rolling Swing Points
        self._dataframe["adj close"].rolling(self._window_size).apply(self._calc_hlsp)

        # Mark Swing Points into the dataframe
        self._dataframe["sp"] = self._swing_points

        # Since High and Low swing points are
        # based on the difference between three
        # consecutive ASI values, we need to shift
        # the SP column by one to get the correct signal
        self._dataframe["sp"] = self._dataframe["sp"].shift(1)

        # Drop swing index, previous open and previous close columns
        self._dataframe.drop(columns=["si", "prev_open", "prev_close"], inplace=True)

    def _calc_si(self, series: pd.Series) -> float:
        """
        Calculate rolling swing index for a given window.

        :param series: Series which is used for indexing out rolling window.
        :returns: Latest calculated entry from processed window.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[series.index]

        # Get current open, high, low, close
        curr_open: float = rolling_df.iloc[-1]["adj open"]
        curr_high: float = rolling_df.iloc[-1]["adj high"]
        curr_low: float = rolling_df.iloc[-1]["adj low"]
        curr_close: float = rolling_df.iloc[-1]["adj close"]

        # Get previous open, close
        prev_open: float = rolling_df.iloc[-1]["prev_open"]
        prev_close: float = rolling_df.iloc[-1]["prev_close"]

        # Calculate absolute differences
        # as the basis of weighted True Range:
        # max(|Ht - Ct-1|, |Lt - Ct-1|, |Ht - Lt|)
        # Kaufman, Trading Systems and Methods, 2020, p.174
        absolute_differences = [
            abs(difference)
            for difference in [
                curr_high - prev_close,
                curr_low - prev_close,
                curr_high - curr_low,
            ]
        ]

        # Get the highest value out of the three
        highest_value = max(absolute_differences)

        # Determine the index of the highest value
        # To decide which weighted True Range calculation to use
        highest_value_index = absolute_differences.index(highest_value)

        # Calculate K: the highest value of the three differences
        highest_difference = max(absolute_differences)

        # Calculate weighted TR using one of
        # the methods based on highest value index
        weighted_true_range = self._calc_wtr(
            highest_value_index,
            curr_high,
            curr_low,
            prev_close,
            prev_open,
        )

        # Finally, calculate Wilders Swing Index as:
        # SI = 50 * (((Ct - Ct-1) + 0.50(Ct - Ot) + 0.25(Ct-1 - Ot-1)) / TRt) * Kt  # noqa: ERA001, E501
        return (
            50
            * (
                (
                    (curr_close - prev_close)
                    + (0.50 * (curr_close - curr_open))
                    + (0.25 * (prev_close - prev_open))
                )
                / weighted_true_range
            )
            * highest_difference
        )

    def _calc_asi(self, series: pd.Series) -> float:
        """
        Calculate rolling accumulated swing index for a given window.

        :param series: Series which is used for indexing out rolling window.
        :returns: Latest calculated entry from processed window.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[series.index]

        # Calculate ASI by summing
        # as we only need the last value
        return rolling_df["si"].sum()

    def _calc_hlsp(self, series: pd.Series) -> float:
        """
        Calculate rolling high/low swing point for a given window.

        High/Low Swing Point:
        Any day on which the ASI is higher/lower
        than both the previous and the following day
        Kaufman, Trading Systems and Methods, 2020, p.175

        :param series: Series which is used for indexing out rolling window.
        :returns: Latest calculated entry from processed window.
        """

        # Slice out a chunk of dataframe to work with
        rolling_df = self._dataframe.loc[series.index]

        # Get the last 3 ASI entries
        # where left: t-2, middle: t-1, right: t
        left, middle, right = list(
            rolling_df.iloc[self._window_size - 3 :]["asi"],
        )

        # If middle ASI is higher than it's neighbors (HSP)
        if middle > left and middle > right:
            # Append positive float to the list
            self._swing_points.append(self.HIGH_SWING_POINT)

        # If middle ASI is lower than it's neighbors (LSP)
        elif middle < left and middle < right:
            # Append negative float to the list
            self._swing_points.append(self.LOW_SWING_POINT)

        else:
            # Otherwise, append falsy float
            self._swing_points.append(0.0)

        # Return dummy value
        return 0.0

    def _calc_wtr(
        self,
        diff_index: int,
        high: float,
        low: float,
        prev_close: float,
        prev_open: float,
    ) -> float:
        """
        Calculate weighted True Range.

        Wilder's Swing Index uses weighted version of True Range.
        Thus, we define several methods to calculate it based on
        the index of the highest absolute difference.

        :param diff_index: Index of the highest absolute difference.
        :param high: Current high price.
        :param low: Current low price.
        :param prev_close: Previous close price.
        :param prev_open: Previous open price.
        :returns: Calculated weighted True Range.
        """

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
