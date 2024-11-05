import pandas as pd

from apollo.core.calculations.base_calculator import BaseCalculator
from apollo.settings import MISSING_DATA_PLACEHOLDER


class CombinatoryFuturesPatternsCalculator(BaseCalculator):
    """
    Combinatory Futures Patterns Calculator.

    Calculates following bullish and bearish patterns for S&P 500 Futures:

    * Morning | Evening Star
    * Bullish | Bearish Engulfing
    * Three White | Black Soldiers (Crows)

    Kaufman, Trading Systems and Methods, 2020, 6th ed.
    """

    # Constant to
    # represent no pattern
    NO_PATTERN: float = 0.0

    # Constant to
    # represent bullish pattern
    BULLISH_PATTERN: float = 1.0

    # Constant to
    # represent bearish pattern
    BEARISH_PATTERN: float = -1.0

    def __init__(
        self,
        dataframe: pd.DataFrame,
        window_size: int,
        doji_threshold: float,
    ) -> None:
        """
        Construct Combinatory Futures Patterns Calculator.

        :param dataframe: Dataframe to calculate Combinatory Patterns for.
        :param window_size: Size of the window for Combinatory Patterns calculation.
        :param doji_threshold: Threshold for identifying candlestick formation as Doji.

        NOTE: even though we accept window_size parameter,
        calculator does not perform any rolling calculations.
        """

        super().__init__(dataframe, window_size)

        self._doji_threshold = doji_threshold

    def calculate_combinatory_futures_patterns(self) -> None:
        """Calculate Combinatory Futures Patterns."""

        # Since we are working with multiple
        # data sources, there is no guarantee that
        # the data is present for all the rows in the dataframe
        # We, therefore, can calculate only over present data points,
        # otherwise, the strategy using the results will drop missing rows

        # Mark patterns to the dataframe
        self._dataframe["spf_ep"] = self.NO_PATTERN
        self._dataframe["spf_sp"] = self.NO_PATTERN
        self._dataframe["spf_tp"] = self.NO_PATTERN

        # Initialize necessary columns with 0
        self._dataframe["spf_open_tm1"] = 0.0
        self._dataframe["spf_open_tm2"] = 0.0

        self._dataframe["spf_close_tm1"] = 0.0
        self._dataframe["spf_close_tm2"] = 0.0

        # Shift open and close to T-1 and T-2
        self._dataframe.loc[
            self._dataframe["spf open"] != MISSING_DATA_PLACEHOLDER,
            "spf_open_tm1",
        ] = self._dataframe["spf open"].shift(1)

        self._dataframe.loc[
            self._dataframe["spf open"] != MISSING_DATA_PLACEHOLDER,
            "spf_open_tm2",
        ] = self._dataframe["spf open"].shift(2)

        self._dataframe.loc[
            self._dataframe["spf close"] != MISSING_DATA_PLACEHOLDER,
            "spf_close_tm1",
        ] = self._dataframe["spf close"].shift(1)

        self._dataframe.loc[
            self._dataframe["spf close"] != MISSING_DATA_PLACEHOLDER,
            "spf_close_tm2",
        ] = self._dataframe["spf close"].shift(2)

        # Precalculate candle midpoint necessary for stars
        open_on_close_midpoint_tm2 = (
            self._dataframe["spf_open_tm2"] + self._dataframe["spf_close_tm2"]
        ) / 2

        # Calculate bullish engulfing
        bullish_engulfing = (
            # Open at T is below the close at T-1
            # Candle opened below the close of the previous candle
            (self._dataframe["spf open"] < self._dataframe["spf_open_tm1"])
            # Close at T is above the open at T-1
            # Candle closed above the open of the previous candle
            & (self._dataframe["spf close"] > self._dataframe["spf_close_tm1"])
            # Close at T is above the open at T
            # Candle closed in positive territory
            & (self._dataframe["spf close"] > self._dataframe["spf open"])
        )

        # Calculate bearish engulfing
        bearish_engulfing = (
            # Open at T is above the close at T-1
            # Candle opened above the close of the previous candle
            (self._dataframe["spf open"] > self._dataframe["spf_open_tm1"])
            # Close at T is below the open at T-1
            # Candle closed below the open of the previous candle
            & (self._dataframe["spf close"] < self._dataframe["spf_close_tm1"])
            # Close at T is below the open at T
            # Candle closed in negative territory
            & (self._dataframe["spf close"] < self._dataframe["spf open"])
        )

        # Calculate bullish morning star
        bullish_morning_star = (
            # Close at T-2 is below the open at T-2
            # Candle at T-2 closed in negative territory
            (self._dataframe["spf_close_tm2"] < self._dataframe["spf_open_tm2"])
            &
            # Difference between close at T-1 and
            # open at T-1 is less than Doji threshold
            # Previous candle closed in neutral territory
            (
                abs(self._dataframe["spf_close_tm1"] - self._dataframe["spf_open_tm1"])
                / self._dataframe["spf_open_tm1"]
                < self._doji_threshold
            )
            &
            # Close at T is above the open at T
            # Candle closed in positive territory
            (self._dataframe["spf close"] > self._dataframe["spf open"])
            &
            # Close at T is above the midpoint of T-2 candle
            (self._dataframe["spf close"] > open_on_close_midpoint_tm2)
        )

        # Calculate bearish evening star
        bearish_evening_star = (
            # Close at T-2 is above the open at T-2
            # Candle at T-2 closed in positive territory
            (self._dataframe["spf_close_tm2"] > self._dataframe["spf_open_tm2"])
            &
            # Difference between close at T-1 and
            # open at T-1 is less than Doji threshold
            # Previous candle closed in neutral territory
            (
                abs(self._dataframe["spf_close_tm1"] - self._dataframe["spf_open_tm1"])
                / self._dataframe["spf_open_tm1"]
                < self._doji_threshold
            )
            &
            # Close at T is below the open at T
            # Candle closed in negative territory
            (self._dataframe["spf close"] < self._dataframe["spf open"])
            &
            # Close at T is below the midpoint of T-2 candle
            (self._dataframe["spf close"] < open_on_close_midpoint_tm2)
        )

        # Calculate three white soldiers
        three_white_soldiers = (
            # Three consecutive positive closes
            (self._dataframe["spf close"] > self._dataframe["spf open"])
            & (self._dataframe["spf_close_tm1"] > self._dataframe["spf_open_tm1"])
            & (self._dataframe["spf_close_tm2"] > self._dataframe["spf_open_tm2"])
            &
            # Each candle closes higher than the previous candle's close
            (self._dataframe["spf close"] > self._dataframe["spf_close_tm1"])
            & (self._dataframe["spf_close_tm1"] > self._dataframe["spf_close_tm2"])
            &
            # Each candle opens within or near the previous candle's body
            # NOTE: this is a reversed version of the original definition
            # Open must be within the previous candle's body to avoid gaps
            (self._dataframe["spf open"] <= self._dataframe["spf_close_tm1"])
            & (self._dataframe["spf_open_tm1"] <= self._dataframe["spf_close_tm2"])
        )

        # Calculate three black soldiers
        three_black_soldiers = (
            # Three consecutive negative closes
            (self._dataframe["spf close"] < self._dataframe["spf open"])
            & (self._dataframe["spf_close_tm1"] < self._dataframe["spf_open_tm1"])
            & (self._dataframe["spf_close_tm2"] < self._dataframe["spf_open_tm2"])
            &
            # Each candle closes lower than the previous candle's close
            (self._dataframe["spf close"] < self._dataframe["spf_close_tm1"])
            & (self._dataframe["spf_close_tm1"] < self._dataframe["spf_close_tm2"])
            &
            # Each candle opens within or near the previous candle's body
            # NOTE: this is a reversed version of the original definition
            # Open must be within the previous candle's body to avoid gaps
            (self._dataframe["spf open"] >= self._dataframe["spf_close_tm1"])
            & (self._dataframe["spf_open_tm1"] >= self._dataframe["spf_close_tm2"])
        )

        # Mark engulfing patterns to the dataframe
        self._dataframe.loc[bullish_engulfing, "spf_ep"] = self.BULLISH_PATTERN
        self._dataframe.loc[bearish_engulfing, "spf_ep"] = self.BEARISH_PATTERN

        # Mark star patterns to the dataframe
        self._dataframe.loc[bullish_morning_star, "spf_sp"] = self.BULLISH_PATTERN
        self._dataframe.loc[bearish_evening_star, "spf_sp"] = self.BEARISH_PATTERN

        # Mark three patterns to the dataframe
        self._dataframe.loc[three_white_soldiers, "spf_tp"] = self.BULLISH_PATTERN
        self._dataframe.loc[three_black_soldiers, "spf_tp"] = self.BEARISH_PATTERN

        # Shift engulfing pattern by one observation
        self._dataframe["spf_ep_tm1"] = self._dataframe["spf_ep"].shift(1)

        # Shift star pattern by one observation
        self._dataframe["spf_sp_tm1"] = self._dataframe["spf_sp"].shift(1)

        # Drop unnecessary columns
        self._dataframe.drop(
            columns=["spf_open_tm1", "spf_open_tm2", "spf_close_tm1", "spf_close_tm2"],
            inplace=True,
        )
